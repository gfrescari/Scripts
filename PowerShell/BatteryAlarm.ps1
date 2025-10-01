Clear-Host
Write-Host "---------------------------------------------"
Write-Host "Battery Alarm Check Every 5 Minutes" -ForegroundColor Cyan
Write-Host "---------------------------------------------"


$sp = New-Object -ComObject SAPI.SpVoice
while(1){
    $batt=(Get-WmiObject win32_battery).estimatedChargeRemaining;
    if ($batt -gt 90){
        for ($i=0;$i -le 2;$i++){$sp.Speak("Battery almost full at $batt%") | Out-Null}
        Write-Host "Battery was $batt% at $(Get-Date -Format 'HH:mm:ss')"
    }
    elseif($batt -lt 25){
        for ($i=0;$i -le 2;$i++){$sp.Speak("Battery low at $batt%") | Out-Null}
        Write-Host "Battery was $batt% at $(Get-Date -Format 'HH:mm:ss')"
    }
    elseif($batt -gt 47 -and $batt -lt 53){
        for ($i=0;$i -le 2;$i++){$sp.Speak("Battery at $batt%") | Out-Null}
        Write-Host "Battery was $batt% at $(Get-Date -Format 'HH:mm:ss')"
    }
    Start-Sleep -Seconds 300
}

