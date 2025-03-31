# -*- mode: python ; coding: utf-8 -*-

# Importações necessárias
import os
import shutil

#from PyInstaller.utils.hooks import collect_data_files

# Defina o caminho para o arquivo de configuração
config_file = 'configuracao.json'

# Defina as seguintes variáveis para seu projeto
entry_point = 'main.py'
project = 'Colocar_COND_EM_GRUPO'
exe_name = f'{project}'


# Gera dinamicamente o arquivo de versão com base no __version_info__
from version import __version__, __version_info__

version_file_content = f"""
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=({', '.join(__version_info__)}, 0),
        prodvers=({', '.join(__version_info__)}, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904B0',
                    [
                        StringStruct(u'CompanyName', u'Estasa'),
                        StringStruct(u'FileVersion', u'{__version__}'),
                        StringStruct(u'InternalName', u'{exe_name}'),
                        StringStruct(u'LegalCopyright', u'Copyright (c) 2024'),
                        StringStruct(u'OriginalFilename', u'{exe_name}.exe'),
                        StringStruct(u'ProductName', u'{exe_name}'),
                        StringStruct(u'ProductVersion', u'{__version__}')
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)
"""

# Escreve o conteúdo no arquivo temporário
version_file_path = "version_info.txt"
with open(version_file_path, "w") as vf:
    vf.write(version_file_content)



# Função para limpar subpastas indesejadas na pasta 'dist'
def clean_dist():

    dist_path = 'dist'
    
    # Verifica se o diretório 'dist' existe
    if os.path.exists(dist_path):

        # Lista todas as subpastas e arquivos no diretório 'dist'
        for item in os.listdir(dist_path):
            item_path = os.path.join(dist_path, item)
            # Remove subpastas ou arquivos que não são o executável principal
            if item != f'{exe_name}.exe':
                shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)

a = Analysis(
    [entry_point],
    pathex=[],
    binaries=[],
    datas=[(config_file, '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=exe_name,
    version=version_file_path,  # Use o arquivo de versão gerado
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Coleta todos os arquivos necessários
coll = COLLECT(
            exe,
            a.binaries,
            a.zipfiles,
            a.datas,       # Inclui os dados coletados, incluindo o arquivo de configuração
            strip=False,
            upx=True,
            name=exe_name
)

# Chama a função de limpeza após a coleta
clean_dist()
