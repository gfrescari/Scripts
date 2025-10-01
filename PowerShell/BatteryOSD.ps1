Add-Type -AssemblyName System.Windows.Forms
$form = New-Object System.Windows.Forms.Form -Property @{TopMost=$true}
$form.TransparencyKey = $form.BackColor
$form.WindowState = 'Maximized'
$form.FormBorderStyle = 'None'
$label = New-Object System.Windows.Forms.Label
$label.Font = New-Object System.Drawing.Font ($label.Font.FontFamily, 20,[System.Drawing.FontStyle]::Bold)
$label.ForeColor = [System.Drawing.Color]::FromKnownColor('Green')
$label.AutoSize = $true
$label.Add_Click({$form.Close()})
$form.Controls.Add($label)
$Timer = New-Object System.Windows.Forms.Timer
$Timer.Interval = 120000
$Timer.Add_Tick( {GetBattery $label})
$Timer.Enabled = $True
[Windows.Forms.Application]::Run($form)
