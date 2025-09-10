# Font Converter

무더기 폰트 포맷 변경하기 귀찮아서 맹근 스크립트

TTF, WOFF, WOFF2 포맷 간에 폰트 파일 변환해 줌. 하나씩 변환하는 것도 되고, 폴더 통째로 한 방에 변환하는 것도 됨. 끝.

## 설치

### 방법 1: 직접 설치
```bash
pip3 install fonttools brotli cu2qu
```

### 방법 2: requirements.txt 사용
```bash
pip3 install -r requirements.txt
```

- brotli는 woff2 쓸 때 필요함
- cu2qu는 OTF → TTF 진짜 변환할 때 필요함 (안 깔아도 동작은 됨)

## 사용법

### 파일 하나만 변환

```bash
# 기본 (같은 폴더에 새 파일 생성)
python3 fc.py -f font.ttf -t woff

# 출력 파일명 지정
python3 fc.py -f font.ttf -o mynewfont.woff -t woff
```

### 폴더 통째로 변환

```bash
# 같은 위치에 변환 (원본과 같은 포맷은 알아서 스킵)
python3 fc.py -d ./fonts -t woff2

# 다른 폴더로 출력
python3 fc.py -d ./fonts -o ./converted -t woff2
```

### 덮어쓰기

기본적으로 이미 있는 파일/폴더는 안 건드림. 덮어쓰려면 `--force` 붙여야 됨.

```bash
python3 fc.py -f font.ttf -o existing.woff -t woff --force
python3 fc.py -d ./fonts -o ./existing_folder -t woff2 --force
```

## 옵션

- `-f, --file`: 변환할 파일 하나
- `-d, --directory`: 변환할 폴더 (하위 폴더까지 다 뒤짐)
- `-o, --output`: 출력 파일/폴더 경로
- `-t, --target`: 변환할 포맷 (ttf, woff, woff2 중 택1)
- `--force`: 이미 있는 거 덮어쓰기

## 주의

- **OTF → TTF 변환**: cu2qu 깔려있으면 CFF → TrueType 아웃라인 변환함. 안 깔려있으면 확장자만 바뀜.
- 대소문자 섞인 확장자(.TtF 같은 거)도 알아서 인식함.
- 입력이랑 출력 디렉토리 같게 하면 안 됨. 당연한 거임.

## 예제

```bash
# Noto Sans 폰트 전부 WOFF2로 변환
python3 fc.py -d Noto_Sans -o Noto_Sans_woff2 -t woff2

# 단일 파일 변환
python3 fc.py -f NotoSans-Regular.ttf -t woff

# 이미 있는 폴더에 강제로 덮어쓰기
python3 fc.py -d fonts/ -o output/ -t woff --force
```
