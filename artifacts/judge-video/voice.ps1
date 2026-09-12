$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$veilNarration = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'narration.json') | ConvertFrom-Json
$veilSpeaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$veilSpeaker.SelectVoice('Microsoft Zira Desktop')
$veilSpeaker.Rate = 0
$veilSpeaker.Volume = 100
for ($veilIndex = 0; $veilIndex -lt $veilNarration.Count; $veilIndex++) {
    $veilFile = Join-Path $PSScriptRoot ('voice-{0:D2}.wav' -f ($veilIndex + 1))
    $veilSpeaker.SetOutputToWaveFile($veilFile)
    $veilSpeaker.Speak($veilNarration[$veilIndex].voice)
}
$veilSpeaker.Dispose()
Write-Output 'Generated 13 English voiceover clips.'

