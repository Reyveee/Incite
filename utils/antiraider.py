import os, discord, time, copy
from discord.ext import commands
from discord.utils import get
from discord.ext import menus
from typing import Callable, Optional
from utils.paginator import *

def create_pages(content, rows, maxrows=15, maxpages=10):
    pages = []
    content.description = ""
    thisrow = 0
    rowcount = len(rows)
    for row in rows:
        thisrow += 1
        if len(content.description) + len(row) < 2000 and thisrow < maxrows + 1:
            content.description += f"\n{row}"
            rowcount -= 1
        else:
            thisrow = 1
            if len(pages) == maxpages - 1:
                content.description += f"\n*+ {rowcount} more entries...*"
                pages.append(content)
                content = None
                break

            pages.append(content)
            content = copy.deepcopy(content)
            content.description = f"{row}"
            rowcount -= 1

    if content is not None and not content.description == "":
        pages.append(content)

    return pages

async def send_as_pages(ctx, content, rows, maxrows=10, maxpages=10):
    pages = create_pages(content, rows, maxrows, maxpages)
    source = PageSource(pages)
    paginator = Paginator(source, ctx=ctx)
    await paginator.paginate(ephemeral=True)

class PageSource(menus.PageSource):
    def __init__(self, pages):
        super().__init__(pages, per_page=1)

    async def format_page(self, menu, page):
        return page.description

