import json
import os

import click
import pandas as pd
from dotenv import load_dotenv

from .dart import OpenDartReader

load_dotenv()

_HELP = dict(help_option_names=['-h', '--help'])


def output_result(data, pretty=False):
    """Helper to output results in JSON (default) or pretty text."""
    if isinstance(data, (pd.DataFrame, pd.Series)):
        # Format datetime columns to string for better JSON/Text output
        if isinstance(data, pd.DataFrame):
            for col in data.select_dtypes(include=['datetime64']).columns:
                # If all times are 00:00:00, just show YYYY-MM-DD
                if (data[col].dt.hour == 0).all() and (data[col].dt.minute == 0).all():
                    data[col] = data[col].dt.strftime('%Y-%m-%d')
                else:
                    data[col] = data[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        else: # Series
            if pd.api.types.is_datetime64_any_dtype(data):
                if data.hour == 0 and data.minute == 0:
                    data = data.strftime('%Y-%m-%d')
                else:
                    data = data.strftime('%Y-%m-%d %H:%M:%S')

        if isinstance(data, pd.DataFrame):
            if pretty:
                click.echo(data.to_string())
            else:
                click.echo(data.to_json(orient='records', force_ascii=False, indent=2))
        else: # Series
            if pretty:
                click.echo(data.to_string())
            else:
                click.echo(json.dumps(data.to_dict(), ensure_ascii=False, indent=2))
    elif isinstance(data, dict):
        if pretty:
            click.echo(pd.Series(data).to_string())
        else:
            click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        click.echo(data)


@click.group(context_settings=_HELP)
@click.option('--api-key', envvar='DART_API_KEY', help='DART API Key')
@click.pass_context
def main(ctx, api_key):
    """OpenDartReader CLI - Access DART disclosures easily."""
    if not api_key:
        click.echo("Error: API Key is required. Set DART_API_KEY env var or use --api-key.")
        ctx.exit(1)
    ctx.obj = {
        'dart': OpenDartReader(api_key)
    }

@main.command(context_settings=_HELP)
@click.argument('corp', required=False)
@click.option('-s', '--start', help='Start date (YYYY-MM-DD)')
@click.option('-e', '--end', help='End date (YYYY-MM-DD)')
@click.option('-k', '--kind', default='', help='Report kind (A, B, C, D, E, F, G, H, I, J)')
@click.option('--kind-detail', default='', help='Report kind detail')
@click.option('--final/--no-final', default=True, help='Final report only (default True)')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def list(ctx, corp, start, end, kind, kind_detail, final, pretty):
    """Search disclosure list for a corporation. If CORP is omitted, returns all.

    With neither --start nor --end, the query range is the past year through today.
    """
    dart = ctx.obj['dart']
    df = dart.list(corp, start, end, kind, kind_detail, final)
    output_result(df, pretty)

@main.command(context_settings=_HELP)
@click.argument('corp')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def company(ctx, corp, pretty):
    """Get company overview."""
    dart = ctx.obj['dart']
    info = dart.company(corp)
    output_result(info, pretty)

@main.command('company-by-name', context_settings=_HELP)
@click.argument('name')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def company_by_name(ctx, name, pretty):
    """Search companies by name and get overview."""
    dart = ctx.obj['dart']
    info = dart.company_by_name(name)
    output_result(info, pretty)

@main.command(context_settings=_HELP)
@click.argument('corp')
@click.argument('year')
@click.option('--report', default='11011', help='Report code (11011: Business, 11012: Half, 11013: Q1, 11014: Q3)')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def finstate(ctx, corp, year, report, pretty):
    """Get financial statements."""
    dart = ctx.obj['dart']
    df = dart.finstate(corp, year, report)
    output_result(df, pretty)

@main.command(context_settings=_HELP)
@click.argument('corp')
@click.argument('keyword')
@click.argument('year')
@click.option('--report', default='11011', help='Report code (11011: Business, 11012: Half, 11013: Q1, 11014: Q3)')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def report(ctx, corp, keyword, year, report, pretty):
    """Get specific report item (e.g. '배당', '직원')."""
    dart = ctx.obj['dart']
    df = dart.report(corp, keyword, year, report)
    output_result(df, pretty)

@main.command(context_settings=_HELP)
@click.argument('corp')
@click.argument('keyword')
@click.option('-s', '--start', help='Start date')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def event(ctx, corp, keyword, start, pretty):
    """Get major event info (e.g. '유상증자')."""
    dart = ctx.obj['dart']
    df = dart.event(corp, keyword, start)
    output_result(df, pretty)

@main.command(context_settings=_HELP)
@click.argument('rcp_no')
@click.pass_context
def document(ctx, rcp_no):
    """Download disclosure document as .html file."""
    dart = ctx.obj['dart']
    xml_text = dart.document(rcp_no)
    filename = f"{rcp_no}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_text)
    click.echo(f"Saved: {filename}")

@main.command('document-all', context_settings=_HELP)
@click.argument('rcp_no')
@click.pass_context
def document_all(ctx, rcp_no):
    """Download all disclosure documents for a receipt number."""
    dart = ctx.obj['dart']
    xml_text_list = dart.document_all(rcp_no)
    for i, xml_text in enumerate(xml_text_list, 1):
        filename = f"{rcp_no}_{i:02d}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_text)
        click.echo(f"Saved: {filename}")

@main.command(context_settings=_HELP)
@click.argument('url')
@click.argument('filename')
@click.pass_context
def download(ctx, url, filename):
    """Download a file from a URL."""
    dart = ctx.obj['dart']
    fn = dart.download(url, filename)
    click.echo(f"Downloaded: {fn}")

@main.command(context_settings=_HELP)
@click.argument('corp')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def shareholders(ctx, corp, pretty):
    """Get major shareholders."""
    dart = ctx.obj['dart']
    df = dart.major_shareholders(corp)
    output_result(df, pretty)

@main.command('find-corp-code', context_settings=_HELP)
@click.argument('corp')
@click.pass_context
def find_corp_code(ctx, corp):
    """Find corporation code by name or stock code."""
    dart = ctx.obj['dart']
    code = dart.find_corp_code(corp)
    if code:
        click.echo(code)
    else:
        click.echo(f"Error: Could not find corporation code for '{corp}'")
        ctx.exit(1)

@main.command('finstate-xml', context_settings=_HELP)
@click.argument('rcp_no')
@click.pass_context
def finstate_xml(ctx, rcp_no):
    """Download XBRL financial statement as .zip file."""
    dart = ctx.obj['dart']
    filename = f"XBRL_{rcp_no}.zip"
    dart.finstate_xml(rcp_no, save_as=filename)
    click.echo(f"Saved: {filename}")

@main.command('sub-docs', context_settings=_HELP)
@click.argument('rcp_no')
@click.option('--match', help='Filter sub-documents by title')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def sub_docs(ctx, rcp_no, match, pretty):
    """Get sub-documents list (title and URL)."""
    dart = ctx.obj['dart']
    df = dart.sub_docs(rcp_no, match=match)
    output_result(df, pretty)

@main.command('attach-files', context_settings=_HELP)
@click.argument('rcp_no')
@click.pass_context
def attach_files(ctx, rcp_no):
    """Download all attachment files for a receipt number."""
    dart = ctx.obj['dart']
    files_dict = dart.attach_files(rcp_no)
    if not files_dict:
        click.echo("No attachment files found.")
        return
    for fname, url in files_dict.items():
        fn = dart.download(url, fname)
        click.echo(f"Downloaded: {fn}")

@main.command('list-presenter', context_settings=_HELP)
@click.argument('presenter')
@click.option('-s', '--start', help='Start date (YYYY-MM-DD)')
@click.option('-e', '--end', help='End date (YYYY-MM-DD)')
@click.option('--type', 'report_type', default='지분공시', help='Report type')
@click.option('--final/--no-final', default=True, help='Final report only')
@click.option('-p', '--pretty', is_flag=True, help='Pretty print output (human readable)')
@click.pass_context
def list_presenter(ctx, presenter, start, end, report_type, final, pretty):
    """Search disclosures by presenter name."""
    dart = ctx.obj['dart']
    df = dart.list_presenter(presenter, start, end, report_type, final)
    output_result(df, pretty)

if __name__ == '__main__':
    main()
