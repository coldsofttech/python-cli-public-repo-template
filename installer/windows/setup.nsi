; NSIS installer for the command line (example-cli.exe), example-cli-<version>-setup.exe.
; Windows only.
;
; Pages: license > install mode (this user or all users) > folder > tasks (PATH) > install. The
; uninstaller removes what setup installed and the PATH entry.
;
; installer/scripts/build.py passes these with /D:
;
;   GUID            stable id of the product, from installer/build.toml (never changes)
;   APP_NAME, APP_VERSION (APP_VERSION_NUMERIC "0.1.0.0" is derived if not given)
;   STAGE_DIR       the PyInstaller folder: the executable and lib\
;   CLI_EXE         the program, e.g. "example-cli.exe"
;   CLI_VERSION     its version (APP_VERSION is the setup's own)
;   OUT_FILE        the installer to write
;   PUBLISHER, URL, ICON_FILE (.ico), LICENSE_FILE   optional
;   SUPPORT_URL, UPDATE_URL   optional: the support page and the release notes (Apps & features)
;   INSTALL_DIR     folder under Program Files (or Programs for one user), e.g. "Vendor\Product";
;                   INSTALL_DIR_DEPTH is its number of parts, so the uninstaller can remove the
;                   empty parent folders too.
;   START_MENU_DIR  Start Menu folder, e.g. "Vendor\Product" (default APP_NAME);
;                   START_MENU_DIR_DEPTH is its number of parts, as for INSTALL_DIR.
;   HEADER_IMAGE (.bmp, 150x57), WELCOME_IMAGE (.bmp, 164x314)   optional, from brand/
;   USER_DATA_DIR   optional: folder with settings and data; the uninstaller asks before removing it
;
; Silent use: Setup.exe /S [/allusers | /currentuser] [/NOPATH] [/D=C:\folder]
;             uninstall.exe /S [/PURGE]
;             (/PURGE also removes USER_DATA_DIR)
; The default is a per-user install; "all users" needs administrator rights (UAC). Running setup
; again replaces the installed version.

!ifndef GUID
  !error "Pass /DGUID=... (the guid in installer/build.toml; scripts/build.py does)."
!endif
!ifndef APP_NAME
  !error "Pass /DAPP_NAME=... (installer/scripts/build.py does)."
!endif
!ifndef APP_VERSION
  !error "Pass /DAPP_VERSION=..."
!endif
!ifndef STAGE_DIR
  !error "Pass /DSTAGE_DIR=... (the PyInstaller folder)."
!endif
!ifndef CLI_EXE
  !error "Pass /DCLI_EXE=..."
!endif
!ifndef CLI_VERSION
  !error "Pass /DCLI_VERSION=..."
!endif
!ifndef OUT_FILE
  !error "Pass /DOUT_FILE=..."
!endif
!ifndef APP_VERSION_NUMERIC
  !define APP_VERSION_NUMERIC "${APP_VERSION}.0"
!endif
!ifndef PUBLISHER
  !define PUBLISHER "${APP_NAME}"
!endif
!ifndef INSTALL_DIR
  !define INSTALL_DIR "${APP_NAME}"
!endif
!ifndef INSTALL_DIR_DEPTH
  !define INSTALL_DIR_DEPTH 1
!endif
!ifndef START_MENU_DIR
  !define START_MENU_DIR "${APP_NAME}"
!endif
!ifndef START_MENU_DIR_DEPTH
  !define START_MENU_DIR_DEPTH 1
!endif
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${GUID}"
!define UNINSTALLER "uninstall.exe"
!define APP_KEY "Software\${APP_NAME}"

Name "${APP_NAME}"
OutFile "${OUT_FILE}"
Unicode true
; The marker is still in $INSTDIR in .onInit unless the user gave /D=folder.
!define NO_INSTDIR "<default folder>"
InstallDir "${NO_INSTDIR}"
SetCompressor /SOLID lzma
BrandingText "${APP_NAME} ${APP_VERSION}"
ManifestDPIAware true
ManifestSupportedOS Win10

VIProductVersion "${APP_VERSION_NUMERIC}"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "FileDescription" "${APP_NAME} setup"
VIAddVersionKey "CompanyName" "${PUBLISHER}"
VIAddVersionKey "LegalCopyright" "${PUBLISHER}"

; ---- install mode: this user (default) or all users --------------------------------------------
; Highest: an administrator is asked once (UAC) at start; a standard user runs unelevated and is
; asked for an administrator only after choosing "all users".
!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_INSTALLMODE_ALLOW_ELEVATION
!define MULTIUSER_INSTALLMODE_DEFAULT_CURRENTUSER
!define MULTIUSER_USE_PROGRAMFILES64
!define MULTIUSER_INSTALLMODE_INSTDIR "${INSTALL_DIR}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${APP_KEY}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallLocation"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "${APP_KEY}"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "InstallLocation"

!include MUI2.nsh
!include MultiUser.nsh
!include FileFunc.nsh
!include LogicLib.nsh
!include nsDialogs.nsh

!insertmacro GetParameters
!insertmacro GetOptions
!insertmacro un.GetParameters
!insertmacro un.GetOptions

!ifdef ICON_FILE
  !define MUI_ICON "${ICON_FILE}"
  !define MUI_UNICON "${ICON_FILE}"
!endif
!ifdef HEADER_IMAGE
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "${HEADER_IMAGE}"
  !define MUI_HEADERIMAGE_UNBITMAP "${HEADER_IMAGE}"
!endif
!ifdef WELCOME_IMAGE
  !define MUI_WELCOMEFINISHPAGE_BITMAP "${WELCOME_IMAGE}"
  !define MUI_UNWELCOMEFINISHPAGE_BITMAP "${WELCOME_IMAGE}"
!endif
!define MUI_ABORTWARNING

Var WantPath
Var CheckPath

; ---- pages ---------------------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
!ifdef LICENSE_FILE
  !insertmacro MUI_PAGE_LICENSE "${LICENSE_FILE}"
!endif
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
Page custom TasksCreate TasksLeave
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ---- install -------------------------------------------------------------------------------------
Section "Command line" SecCli
  SetRegView 64

  ; An upgrade replaces the old files; stale ones from an earlier version must not stay behind.
  RMDir /r "$INSTDIR\lib"

  SetOutPath "$INSTDIR"
  File /r "${STAGE_DIR}\*.*"
  !ifdef LICENSE_FILE
    File "/oname=LICENSE.txt" "${LICENSE_FILE}"
  !endif
  File "${__FILEDIR__}/path.ps1"

  WriteUninstaller "$INSTDIR\${UNINSTALLER}"

  CreateDirectory "$SMPROGRAMS\${START_MENU_DIR}"
  CreateShortcut "$SMPROGRAMS\${START_MENU_DIR}\Uninstall ${APP_NAME}.lnk" "$INSTDIR\${UNINSTALLER}"
  ; A prompt where the command already works, even if it was not added to PATH.
  CreateShortcut "$SMPROGRAMS\${START_MENU_DIR}\${APP_NAME} prompt.lnk" "$SYSDIR\cmd.exe" \
    '/K set "PATH=$INSTDIR;%PATH%"' "$INSTDIR\${CLI_EXE}" 0

  ; Where it is installed (also tells a later setup, and the uninstaller, which mode this was).
  WriteRegStr SHCTX "${APP_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr SHCTX "${APP_KEY}" "CliVersion" "${CLI_VERSION}"

  ; Apps & features
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\${CLI_EXE}"
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "Publisher" "${PUBLISHER}"
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\${UNINSTALLER}"'
  WriteRegStr SHCTX "${UNINSTALL_KEY}" "QuietUninstallString" '"$INSTDIR\${UNINSTALLER}" /S'
  !ifdef URL
    WriteRegStr SHCTX "${UNINSTALL_KEY}" "URLInfoAbout" "${URL}"
  !endif
  !ifdef SUPPORT_URL
    WriteRegStr SHCTX "${UNINSTALL_KEY}" "HelpLink" "${SUPPORT_URL}"
  !endif
  !ifdef UPDATE_URL
    WriteRegStr SHCTX "${UNINSTALL_KEY}" "URLUpdateInfo" "${UPDATE_URL}"
  !endif
  WriteRegDWORD SHCTX "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD SHCTX "${UNINSTALL_KEY}" "NoRepair" 1
SectionEnd

; What the tasks page chose, once the program is in place.
Section "-Tasks" SecTasks
  SetRegView 64
  ${If} $WantPath == 1
    ${If} $MultiUser.InstallMode == "AllUsers"
      StrCpy $0 "Machine"
    ${Else}
      StrCpy $0 "User"
    ${EndIf}
    nsExec::ExecToLog '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive \
      -ExecutionPolicy Bypass -File "$INSTDIR\path.ps1" -Action Add -Scope $0 -Dir "$INSTDIR"'
    Pop $1
    ${If} $1 != 0
      DetailPrint "Could not add $INSTDIR to PATH (code $1)."
    ${Else}
      WriteRegDWORD SHCTX "${APP_KEY}" "OnPath" 1
    ${EndIf}
  ${EndIf}
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD SHCTX "${UNINSTALL_KEY}" "EstimatedSize" "$0"
SectionEnd

; ---- install: start up and pages (after the sections, whose constants they use) -----------------
Function .onInit
  ; MultiUser sets $INSTDIR for the chosen mode and would discard a folder given with /D=, so
  ; keep that folder (anything but the marker below) and put it back afterwards.
  StrCpy $R8 $INSTDIR
  !insertmacro MULTIUSER_INIT
  ${If} $R8 != "${NO_INSTDIR}"
    StrCpy $INSTDIR $R8
  ${EndIf}
  SetRegView 64

  StrCpy $WantPath 1
  ${GetParameters} $R0
  ${GetOptions} $R0 "/NOPATH" $R1
  ${IfNot} ${Errors}
    StrCpy $WantPath 0
  ${EndIf}
  ClearErrors
FunctionEnd

Function TasksCreate
  !insertmacro MUI_HEADER_TEXT "Additional tasks" "Choose what else setup should do."
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}
  ${NSD_CreateCheckbox} 0 10u 100% 12u "Add ${APP_NAME} to PATH, so it runs from any terminal"
  Pop $CheckPath
  ${If} $WantPath == 1
    ${NSD_Check} $CheckPath
  ${EndIf}
  nsDialogs::Show
FunctionEnd

Function TasksLeave
  ${NSD_GetState} $CheckPath $0
  ${If} $0 == ${BST_CHECKED}
    StrCpy $WantPath 1
  ${Else}
    StrCpy $WantPath 0
  ${EndIf}
FunctionEnd

; ---- uninstall -----------------------------------------------------------------------------------
; Only what setup installed is removed, so a folder chosen by hand keeps anything else in it.
Section "Uninstall"
  SetRegView 64
  ReadRegDWORD $1 SHCTX "${APP_KEY}" "OnPath"
  ${If} $1 == 1
    ${If} $MultiUser.InstallMode == "AllUsers"
      StrCpy $0 "Machine"
    ${Else}
      StrCpy $0 "User"
    ${EndIf}
    nsExec::ExecToLog '"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive \
      -ExecutionPolicy Bypass -File "$INSTDIR\path.ps1" -Action Remove -Scope $0 -Dir "$INSTDIR"'
    Pop $1
  ${EndIf}

  RMDir /r "$INSTDIR\lib"
  Delete "$INSTDIR\${CLI_EXE}"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\path.ps1"
  Delete "$INSTDIR\${UNINSTALLER}"
  RMDir "$INSTDIR"
  ; The vendor and product folders above it, only when empty.
  !if ${INSTALL_DIR_DEPTH} >= 2
    RMDir "$INSTDIR\.."
  !endif
  !if ${INSTALL_DIR_DEPTH} >= 3
    RMDir "$INSTDIR\..\.."
  !endif

  RMDir /r "$SMPROGRAMS\${START_MENU_DIR}"
  ; The publisher folder above it, only when empty.
  !if ${START_MENU_DIR_DEPTH} >= 2
    RMDir "$SMPROGRAMS\${START_MENU_DIR}\.."
  !endif
  !if ${START_MENU_DIR_DEPTH} >= 3
    RMDir "$SMPROGRAMS\${START_MENU_DIR}\..\.."
  !endif
  DeleteRegKey SHCTX "${UNINSTALL_KEY}"
  DeleteRegKey SHCTX "${APP_KEY}"

  ; Settings and data stay unless the user opts in (or passes /PURGE when silent).
  !ifdef USER_DATA_DIR
    ${un.GetParameters} $R0
    ${un.GetOptions} $R0 "/PURGE" $R1
    ${IfNot} ${Errors}
      RMDir /r "${USER_DATA_DIR}"
    ${ElseIfNot} ${Silent}
      MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
        "Also remove your ${APP_NAME} settings and data?$\r$\n${USER_DATA_DIR}" IDNO +2
      RMDir /r "${USER_DATA_DIR}"
    ${EndIf}
  !endif
SectionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
  SetRegView 64
FunctionEnd
