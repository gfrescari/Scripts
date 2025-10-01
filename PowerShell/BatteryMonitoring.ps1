Clear-Host

Write-Host "Real-Time Battery Monitor (updates every 5 seconds)" -ForegroundColor Cyan

while ($true) {
    $batteryStatus = Get-WmiObject -Namespace root\wmi -Class BatteryStatus

    if ($batteryStatus) {
        $chargeStatus = if ($batteryStatus.Charging) { "Charging" } elseif ($batteryStatus.DischargeRate -gt 0) { "Discharging" } else { "Idle" }
        $powerDraw = $batteryStatus.DischargeRate
        $powerCharge = $batteryStatus.ChargeRate

        # Convert mW to W if value is present and meaningful
        if ($powerDraw -ne $null -and $powerDraw -ne 0) {
            $powerWatts = [math]::Round($powerDraw / 1000, 2)
        } else {
            $powerWatts = "N/A"
        }

        if ($powerCharge -ne $null -and $powerCharge -ne 0) {
            $powerCharge = [math]::Round($powerCharge / 1000, 2)
        } else {
            $powerCharge = "N/A"
        }

        Clear-Host
        Write-Host "Real-Time Battery Monitor (updates every 5 seconds)" -ForegroundColor Cyan
        Write-Host "---------------------------------------------"
        Write-Host "Status           : $chargeStatus"
        Write-Host "Charge Rate      : $powerCharge W"
        Write-Host "Discharge Rate   : $powerWatts W"
        Write-Host "Time             : $(Get-Date -Format 'HH:mm:ss')"
        Write-Host "---------------------------------------------"
    } else {
        Write-Host "Battery status not available. Your system may not support WMI-based battery telemetry." -ForegroundColor Red
        break
    }

    Start-Sleep -Seconds 5
}
