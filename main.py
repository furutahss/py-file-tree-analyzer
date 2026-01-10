import os
import sys
import argparse
from pathlib import Path

# サイズの単位
UNITS = ['B', 'KB', 'MB', 'GB', 'TB']

# サイズを読みやすい形式に変換
# @param size_bytes: サイズ（バイト単位）
# @return: 読みやすい形式のサイズ文字列
def get_human_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    
    i = 0
    while size_bytes >= 1024 and i < len(UNITS) - 1:
        size_bytes /= 1024.0
        i += 1
    
    # [  10.5MB] のように表示するため、全体で8文字分確保して右寄せ
    return f"{size_bytes:.1f} {UNITS[i]}"

# ディレクトリ内の全ファイルの合計サイズを取得
# @param path: ディレクトリのPathオブジェクト
# @return: 合計サイズ（バイト単位）
def get_dir_size(path):
    try:
        return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    except PermissionError:
        return 0

# ツリー構造を再帰的に生成し、ファイルに書き出す
# @param directory: 対象のPathオブジェクト
# @param file_handle: 書き込み用のファイルハンドル
# @param prefix: ツリーの接頭辞（再帰的に使用）
# @param is_last: 現在のアイテムが最後のアイテムかどうか
# @param root: ルートディレクトリかどうか
# @return None
def generate_tree(directory, file_handle, prefix="", is_last=True, root=False):
    try:
        if directory.is_file():
            size_val = directory.stat().st_size
        else:
            size_val = get_dir_size(directory)
    except PermissionError:
        size_val = 0

    size_str = f"[{get_human_size(size_val):>9}]"
    branch = "" if root else ("└── " if is_last else "├── ")
    
    # 1行分のデータを作成
    line = f"{size_str}  {prefix}{branch}{directory.name}{'/' if directory.is_dir() else ''}\n"
    
    # コンソールとファイルの両方に出力
    print(line, end="")
    file_handle.write(line)

    if directory.is_dir():
        try:
            items = sorted([p for p in directory.iterdir() if not p.name.startswith('.')],
                           key=lambda x: (x.is_file(), x.name.lower()))
            
            if not root:
                prefix += "    " if is_last else "│   "
            
            count = len(items)
            for i, item in enumerate(items):
                generate_tree(item, file_handle, prefix, i == count - 1)
        except PermissionError:
            pass

# メイン処理
def main():
    parser = argparse.ArgumentParser(description="サイズ表示付きディレクトリツリー作成・保存ツール")
    parser.add_argument("path", nargs="?", default=".", help="対象ディレクトリのパス")
    args = parser.parse_args()

    target_path = Path(args.path).expanduser().resolve()
    
    if not target_path.exists():
        print(f"エラー: {target_path} は存在しません。")
        sys.exit(1)

    # 出力ファイル名の決定 (パスの末尾名 + .txt)
    output_filename = f"{target_path.name if target_path.name else 'root'}.txt"

    print(f"📂 スキャン対象: {target_path}")
    print(f"📝 出力ファイル: {output_filename}")
    print("-" * 50)

    with open(output_filename, "w", encoding="utf-8") as f:
        header = f"{'SIZE':>11}  STRUCTURE\n" + ("-" * 50) + "\n"
        print(header, end="")
        f.write(header)
        
        generate_tree(target_path, f, root=True)

    print("-" * 50)
    print(f"✨ 完了しました。結果は '{output_filename}' に保存されました。")

if __name__ == "__main__":
    main()