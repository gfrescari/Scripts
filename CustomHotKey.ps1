$sp2 = New-Object -ComObject SAPI.SpVoice
$key  = [Byte][Char]'K' ## Letter
$key2 = '0x11' ## Ctrl
$key3 = '0x12' ## Alt 
$Signature = @'
    [DllImport("user32.dll", CharSet=CharSet.Auto, ExactSpelling=true)] 
    public static extern short GetAsyncKeyState(int virtualKeyCode); 
'@
Add-Type -MemberDefinition $Signature -Name Keyboard -Namespace PsOneApi
do
{   If( [bool]([PsOneApi.Keyboard]::GetAsyncKeyState($key) -eq -32767 -and 
        [PsOneApi.Keyboard]::GetAsyncKeyState($key2) -eq -32767 -and 
        [PsOneApi.Keyboard]::GetAsyncKeyState($key3) -eq -32767))
        { 
            $batt=(Get-WmiObject win32_battery).estimatedChargeRemaining;$sp2.Speak("Battery at $batt%");
        }
    
      Start-Sleep -Milliseconds 100

} while($true)
