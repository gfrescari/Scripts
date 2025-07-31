Clear-Host

Write-Host "Real-Time Battery Monitor (updates every 5 seconds)" -ForegroundColor Cyan

while ($true) {
    $batteryStatus = Get-WmiObject -Namespace root\wmi -Class BatteryStatus

    if ($batteryStatus) {
        $chargeStatus = if ($batteryStatus.Charging) { "Charging" } elseif ($batteryStatus.DischargeRate -gt 0) { "Discharging" } else { "Idle" }
        $powerDraw = $batteryStatus.DischargeRate

        # Convert mW to W if value is present and meaningful
        if ($powerDraw -ne $null -and $powerDraw -ne 0) {
            $powerWatts = [math]::Round($powerDraw / 1000, 2)
        } else {
            $powerWatts = "N/A"
        }

        Clear-Host
        Write-Host "Real-Time Battery Monitor (updates every 5 seconds)" -ForegroundColor Cyan
        Write-Host "---------------------------------------------"
        Write-Host "Status       : $chargeStatus"
        Write-Host "Power Draw   : $powerWatts W"
        Write-Host "Time         : $(Get-Date -Format 'HH:mm:ss')"
        Write-Host "---------------------------------------------"
    } else {
        Write-Host "Battery status not available. Your system may not support WMI-based battery telemetry." -ForegroundColor Red
        break
    }

    Start-Sleep -Seconds 5
}