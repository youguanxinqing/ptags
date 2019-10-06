#! /usr/bin/env python3

# ptags
#
# Create a tags file for Python programs, usable with vi.
# Tagged are:
# - functions (even inside other defs or classes)
# - classes
# - filenames
# Warns about files it cannot open.
# No warnings about duplicate tags.

import sys, re, os
import subprocess as sp


class CreateTags(object):
    tags = []

    error_files = []
    all_files: int = 0

    expr = r'^[ \t]*(def|class)[ \t]+([a-zA-Z0-9_]+)[ \t]*[:\(]'
    matcher = re.compile(expr)

    @classmethod
    def ct_main(cls, args):
        """
        伪装主函数
        """
        error, search_paths, target_filename = cls.check_input(args)
        if error:
            cls.usage()
            return

        for filename in cls.all_py_files(search_paths):
            cls.treat_file(filename)

        cls.write_tag_file(target_filename)
        cls.end_print()

    @classmethod
    def write_tag_file(cls, target):
        """
        结果写入 tag 文件
        """
        if cls.tags:
            fp = open(target, 'w')
            cls.tags.sort()
            for s in cls.tags: fp.write(s)

    @classmethod
    def all_py_files(cls, paths):
        """
        获取所有指定目录下的 py 文件
        """
        count = 0
        for p in paths:
            res = sp.Popen(f"find {p} -name \*.py", shell=True, stdout=sp.PIPE)
            for pyfile in res.stdout.readlines():
                pyfile = pyfile.decode("utf-8").strip()

                if pyfile:
                    count += 1
                    yield pyfile

        cls.all_files = count

    @classmethod
    def check_input(cls, args):
        """
        根据输入内容，选择处理方式
        """
        if len(args) < 2:
            return True, None, None

        dir_or_file = args[-1]
        if os.path.isdir(dir_or_file):  # eg: ./ptags.py /opt/python/ [targs]
            search_paths, target_filename = args[1:], "tags"
        elif (  # eg: ./python.py [/] tags
                len(args) == 2
                and (not os.path.exists(dir_or_file)
                     or os.path.isfile(dir_or_file))
            ):
            search_paths, target_filename = ["/"], dir_or_file
        else:  # eg: ./python.py /opt /usr ... tags
            search_paths, target_filename  = args[1:-1], args[-1]

        return False, search_paths, target_filename

    @classmethod
    def treat_file(cls, filename):
        # 尝试打开文件
        try:
            fp = open(filename, 'r', errors="ignore")  # 忽略编码错误
        except:
            sys.stderr.write('Cannot open %s\n' % filename)
            return  # 如果打开失败，结束对该文件的后续操作

        # 获取文件名字
        base = os.path.basename(filename)
        if base[-3:] == '.py':
            base = base[:-3]
        # 按规范拼接
        s = base + '\t' + filename + '\t' + '1\n'
        cls.tags.append(s)

        cls.treat_line(fp, filename)

    @classmethod
    def treat_line(cls, fp, filename):
        """
        行匹配
        """
        while 1:

            try:
                line = fp.readline()
            # 避开编码引发的异常
            except UnicodeDecodeError:
                cls.error_files.append(filename)
                continue

            if not line:
                break

            m = cls.matcher.match(line)
            if m:
                content = m.group(0)
                name = m.group(2)
                s = name + '\t' + filename + '\t/^' + content + '/\n'
                cls.tags.append(s)

    @classmethod
    def end_print(cls):
        print(f"{WithColor.green_bold('Success')} is {cls.all_files - len(cls.error_files)},"
              f"{WithColor.red_bold('failure')} is {len(cls.error_files)}")
        if cls.error_files:
            print(f"{WithColor.red_bold('error file:')}")
            for f in cls.error_files:
                print(f)

    @staticmethod
    def usage():

        colorwords = [WithColor.green_bold(w) for w in ("Usage", "search_paths", "target_filename")]

        usage_string = f"""
{colorwords[0]}:
    - ./ptags [search_paths] [target_filename]
    - python ptags [search_paths] [target_filename]
        """
        print(usage_string)

        explain_string = f"""
{colorwords[1]} is some paths of python source code.

{colorwords[2]} is name of tags file, **tags** by default.
        """

        print(explain_string)


class WithColor(object):
    """
    字体着色
    """
    @staticmethod
    def yellow_bold(s):
        return f"\033[1;33m{s}\033[0m"

    @staticmethod
    def red_bold(s):
        return f"\033[1;31m{s}\033[0m"

    @staticmethod
    def green_bold(s):
        return f"\033[1;32m{s}\033[0m"


if __name__ == '__main__':
    CreateTags.ct_main(sys.argv)
