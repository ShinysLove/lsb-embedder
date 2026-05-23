from PIL import Image
import struct
import os

def embed_exe(image_path: str, exe_path: str, output_path: str):
    if not os.path.exists(image_path):
        print(f"[-] Ошибка: '{image_path}' не найден.")
        return
    if not os.path.exists(exe_path):
        print(f"[-] Ошибка: '{exe_path}' не найден.")
        return

    img = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())
    flat = [v for p in pixels for v in p]

    with open(exe_path, 'rb') as f:
        exe_data = f.read()

    payload = struct.pack('>I', len(exe_data)) + exe_data
    binary = ''.join(format(b, '08b') for b in payload)

    if len(binary) > len(flat):
        print(f"[-] Ошибка: изображение слишком маленькое. Требуется минимум {len(binary)//3} пикселей.")
        return

    for i in range(len(binary)):
        flat[i] = (flat[i] & 0xFE) | int(binary[i])

    new_pixels = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path, 'PNG')
    print(f"[+] EXE успешно спрятан в {output_path} ({len(exe_data)} байт)")

def extract_exe(png_path: str, output_path: str):
    if not os.path.exists(png_path):
        print(f"[-] Ошибка: '{png_path}' не найден.")
        return

    img = Image.open(png_path).convert('RGB')
    pixels = list(img.getdata())
    flat = [v for p in pixels for v in p]

    binary = ''.join(str(v & 1) for v in flat)
    byte_arr = bytes(int(binary[i:i + 8], 2) for i in range(0, len(binary), 8))

    if len(byte_arr) < 4:
        print("[-] Ошибка: файл слишком мал или не содержит скрытых данных.")
        return

    exe_size = struct.unpack('>I', byte_arr[:4])[0]
    if exe_size > len(byte_arr) - 4:
        print("[-] Ошибка: повреждённые данные или неверный заголовок размера.")
        return

    exe_data = byte_arr[4:4 + exe_size]
    with open(output_path, 'wb') as f:
        f.write(exe_data)
    print(f"[+] EXE успешно извлечён: {output_path} ({exe_size} байт)")

def main():
    while True:
        print("\n" + "="*45)
        print(" 1 - Вставить EXE в картинку")
        print(" 2 - Извлечь EXE из картинки")
        print(" 0 - Выход")
        print("="*45)

        try:
            choice = int(input("Выберите действие: "))
        except ValueError:
            print("[-] Введите число (0, 1 или 2).")
            continue

        if choice == 0:
            print("Выход...")
            break
        elif choice == 1:
            img_in = input("Путь к картинке: ").strip()
            exe_in = input("Путь к EXE: ").strip()
            out_png = input("Путь для результата: ").strip()
            embed_exe(img_in, exe_in, out_png)
        elif choice == 2:
            png_in = input("Путь к PNG со скрытым EXE [photo_ИФ.png]: ").strip() or "photo_ИФ.png"
            out_exe = input("Путь для извлечённого EXE [restored.exe]: ").strip() or "restored.exe"
            extract_exe(png_in, out_exe)
        else:
            print("[-] Неверный выбор. Введите 0, 1 или 2.")

if __name__ == "__main__":
    main()
