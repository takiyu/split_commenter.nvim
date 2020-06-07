import neovim

import re

# -----------------------------------------------------------------------------
# --------------------------------- Constants ---------------------------------
# -----------------------------------------------------------------------------
DEFAULT_COMMENT_STR = '//'
DEFAULT_N_COL = 80
DEFAULT_SPLIT_CHAR = '-'
SPLIT_CHAR_CANDS = ['-', '=', '*', '#']


# -----------------------------------------------------------------------------
# ----------------------------------- Plugin ----------------------------------
# -----------------------------------------------------------------------------
@neovim.plugin
class SplitCommenterPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.command('MakeSplitComment', sync=True, nargs='?')
    def make_split_comment(self, args):
        # Generate lines
        content_line, _ = self._impl_common(args)

        # Set content line
        row_idx, _ = self.nvim.current.window.cursor
        line_idx = row_idx - 1
        self.nvim.current.buffer[line_idx] = content_line

    @neovim.command('MakeSplitComment3', sync=True, nargs='?')
    def make_split_comment3(self, args):
        # Generate lines
        content_line, splitter_line = self._impl_common(args)

        # Set content line with surrounding lines
        row_idx, _ = self.nvim.current.window.cursor
        line_idx = row_idx - 1
        self.nvim.current.buffer[line_idx] = splitter_line
        self.nvim.current.buffer.append([content_line, splitter_line],
                                        index=line_idx + 1)

    def _impl_common(self, args):
        split_char = DEFAULT_SPLIT_CHAR

        # Get comment string
        comment_str = _obtain_comment_str(self.nvim)

        # Get column number
        n_col = _obtain_n_col(self.nvim)

        # Decide content
        if len(args) == 0:
            content = _extract_line_content(self.nvim, comment_str)
        else:
            content = args[0]

        # Create lines
        content_line = _gen_content_line(comment_str, content, n_col,
                                         split_char)
        splitter_line = _gen_splitter_line(comment_str, n_col, split_char)

        return content_line, splitter_line


# -----------------------------------------------------------------------------
# ------------------------------ Implementation -------------------------------
# -----------------------------------------------------------------------------
def _obtain_comment_str(nvim):
    # Obtain comment string from `caw` plugin.
    try:
        return nvim.eval('b:caw_oneline_comment')
    except Exception:
        return DEFAULT_COMMENT_STR


def _obtain_n_col(nvim):
    # Execute command 'set colorcolumn'
    try:
        n_col_str = nvim.eval('&colorcolumn')
        return int(n_col_str)
    except Exception:
        return DEFAULT_N_COL


def _extract_line_content(nvim, comment_str):
    # Get current line
    line = nvim.current.line         # '  // ---- content ----   '
    # Remove heading spaces
    line = re.sub(r'^\s*', '', line)  # '// ---- content ----   '
    # Remove tailing spaces
    line = re.sub(r'\s*$', '', line)  # '// ---- content ----'
    # Remove comment string
    line = re.sub(f'^{comment_str}', '', line)  # ' ---- content ----'
    # Remove heading spaces
    line = re.sub(r'^\s*', '', line)  # '---- content ----'

    # Decide splitting char
    for split_char in SPLIT_CHAR_CANDS:
        if line.startswith(split_char):
            break
    else:
        split_char = ''
    if split_char:
        # Remove heading splitting chars
        line = re.sub(f'^{split_char}*', '', line)  # ' content ----'
        # Remove tailing splitting chars
        line = re.sub(f'{split_char}*$', '', line)  # ' content '

    # Remove heading spaces
    line = re.sub(r'^\s*', '', line)  # 'content '
    # Remove tailing spaces
    line = re.sub(r'\s*$', '', line)  # 'content'

    return line


def _gen_content_line(comment_str, content, n_col, split_char):
    prefix = comment_str + ' '

    # No content case
    if not content:
        # Generate '// --------'
        return _gen_splitter_line(comment_str, n_col, split_char)

    # Normal case
    content = f' {content} '
    n_splitter = n_col - len(prefix) - len(content)
    splitter1 = '-' * (n_splitter // 2)
    splitter2 = '-' * (n_splitter - n_splitter // 2)
    return f'{prefix}{splitter1}{content}{splitter2}'


def _gen_splitter_line(comment_str, n_col, split_char):
    prefix = comment_str + ' '

    # Generate '// --------'
    n_splitter = n_col - len(prefix)
    splitter = split_char * n_splitter
    return f'{prefix}{splitter}'
