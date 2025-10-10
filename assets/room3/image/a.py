import os

def fix_png_extensions(directory):
    # 디렉토리 내의 모든 파일과 폴더를 순회
    for root, dirs, files in os.walk(directory):
        for file in files:
            # .png.png로 끝나는 파일을 찾음
            if file.endswith('.png.png'):
                # 현재 파일의 전체 경로
                old_path = os.path.join(root, file)
                # 새로운 파일명 (.png.png -> .png)
                new_filename = file[:-4]  # 마지막 .png를 제거
                new_path = os.path.join(root, new_filename)
                
                try:
                    os.rename(old_path, new_path)
                    print(f'Renamed: {old_path} -> {new_path}')
                except Exception as e:
                    print(f'Error renaming {old_path}: {e}')

# 현재 스크립트가 있는 디렉토리에서 시작
current_directory = os.path.dirname(os.path.abspath(__file__))
fix_png_extensions(current_directory)