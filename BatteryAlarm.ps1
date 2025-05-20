$sp = New-Object -ComObject SAPI.SpVoice
while(1){$batt=(Get-WmiObject win32_battery).estimatedChargeRemaining; `
if ($batt -gt 94){ `
$sp.Speak("Battery almost full at $batt%");$sp.Speak("Battery almost full at $batt%");$sp.Speak("Battery almost full at $batt%"); `
} `
elseif($batt -lt 25){ `
$sp.Speak("Battery low at $batt%");$sp.Speak("Battery low at $batt%");$sp.Speak("Battery low at $batt%"); `
} `
elseif($batt -gt 47 -and $batt -lt 53){ `
$sp.Speak("Battery at $batt%");$sp.Speak("Battery at $batt%");$sp.Speak("Battery at $batt%"); `
} `
Start-Sleep -Seconds 300 `
}