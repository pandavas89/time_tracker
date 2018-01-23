# -*- mode: python -*-

block_cipher = None


a = Analysis(['time_tracker.py'],
             pathex=['C:\\Users\\panda\\Google 드라이브\\사민철\\자기 계발\\Python Project\\Time Tracker\\v_0.9.2'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='time_tracker',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
