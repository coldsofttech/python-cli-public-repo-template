# Brand

Sample artwork, so the installers and the Linux packages build out of the box. Replace the files with your own, keeping the names and sizes, or point `[brand]` in `installer/build.toml` at other files.

| File | Used for | Size |
| --- | --- | --- |
| `light/app.ico` | The executable, the Windows setup and the uninstaller | 16 to 256 px in one `.ico` |
| `light/png/app-<size>.png` | The Linux packages (freedesktop `hicolor` icons) | 16, 24, 32, 48, 64, 128, 256 px |
| `dark/nsis/header.bmp` | The Windows setup header | 24-bit BMP, 150x57 |
| `dark/nsis/welcome.bmp` | The Windows setup welcome and finish pages | 24-bit BMP, 164x314 |
