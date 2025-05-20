while ($true) {
    $currentTime = Get-Date -Format "HH:mm"

    if ($currentTime -eq "13:00") {
        Write-Output "Hello World"
        # Sleep for 61 seconds to avoid duplicate messages in the same minute
        Start-Sleep -Seconds 61
    }
    else {
        # Sleep for 30 seconds before checking the time again
        Start-Sleep -Seconds 30
    }
}
