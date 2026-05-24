# Tezkor ishga tushirish (Fast Startup) va hibernatsiyani o‘chirish.
# PowerShell ni "Administrator sifatida ishga tushirish" bilan yurgizing.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power'
if (-not (Test-Path $key)) {
    Write-Error "Registry yo'li topilmadi: $key"
    exit 1
}

Set-ItemProperty -Path $key -Name HiberbootEnabled -Value 0 -Type DWord -Force
$p = Start-Process -FilePath 'powercfg.exe' -ArgumentList '/hibernate', 'off' -Wait -PassThru -NoNewWindow

$hiber = Get-ItemProperty -Path $key -Name HiberbootEnabled
Write-Host "HiberbootEnabled = $($hiber.HiberbootEnabled)  (0 = Tezkor ishga tushirish o‘chiq)"
Write-Host "powercfg /hibernate off exit code: $($p.ExitCode)"
Write-Host "O‘zgarishlar uchun kompyuterni qayta ishga tushiring."
