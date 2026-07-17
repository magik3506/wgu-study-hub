Mascot event voice lines
========================

Six folders, one per event. Put ANY audio files inside — any names, any
count, .wav / .mp3 / .ogg / .m4a all work. The server lists what's on
disk (/api/voicelines) and the mascot picks randomly from that list, so
adding, replacing, or renaming lines needs no rebuild — just restart the
hub.

    assets/voicelines/
      answered_correctly/     a drill answer graded correct
      answered_incorrectly/   graded wrong (skips count as wrong)
      scoring_well/           drill finished above 85%
      scoring_bad/            drill finished below 65%
      general_advice/         10 quiet minutes, repeats while idle
      too_long/               3-hour session nudge (+ banner), every 30 min

Example of what's here today: answered_correctly/answered_correctly_01.wav
… _05.wav.

Missing folders or files are skipped silently. To retime events or change
the score thresholds, edit the constants at the top of web/src/sound.js
(that DOES need an `npm run build` — see the README).
