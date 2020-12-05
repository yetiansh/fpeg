import os
import sys
from argparse import ArgumentParser

from fpeg import jpeg2000_compress, jpeg2000_decompress, fpeg_compress, fpeg_decompress


def compress(args):
  if args.algorithm == "jpeg2000":
    jpeg2000_compress(args)
  else:
    fpeg_compress(args)


def decompress(args):
  if args.algorithm == "jpeg2000":
    jpeg2000_decompress(args)
  else:
    fpeg_decompress(args)


if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument("--chdir", type=str)
  parser.add_argument("--input", type=str)
  parser.add_argument("--output", type=str)
  subparsers = parser.add_subparsers()

  compress_parser = subparsers.add_parser("compress")
  sub_compress_parsers = compress_parser.add_subparsers()
  jpeg2000_compress_parser = sub_compress_parsers.add_parser("jpeg2000")
  jpeg2000_compress_parser.add_argument("--lossy", type=bool, default=True)
  jpeg2000_compress_parser.add_argument("--level", type=int, default=5)
  jpeg2000_compress_parser.add_argument("--depth", type=int, default=8)

  decompress_parser = subparsers.add_parser("decompress")
  sub_decompress_parsers = decompress_parser.add_subparsers()

  args = parser.parse_args(sys.argv[1:])
  if args.chdir:
    os.chdir(args.chdir)

  args.func(args)
