window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext();
var audioInput = null,
realAudioInput = null,
inputPoint = null,
audioRecorder = null;

function gotBuffers(buffers) {
    audioRecorder.exportMonoWAV(doneEncoding);
}

function doneEncoding(soundBlob) {
    document.getElementById("loading").style.display = "block";
    fetch('/audio', {method: "POST", body: soundBlob}).then(response => response.text().then(text => {
        if (text == "ERR"){
            // Handle error
        }
        else{
            document.getElementById("loading").style.display = "none";
            document.getElementById("you-said").innerHTML = text;
            // Refresh images
            document.getElementById("img-waveform").src = "/static/images/waveform.png?t=" + new Date().getTime();
            document.getElementById("img-spectrum").src = "/static/images/spectrum.png?t=" + new Date().getTime();
            document.getElementById("img-spectrogram").src = "/static/images/spectrogram.png?t=" + new Date().getTime();
            document.getElementById("img-mel-spectrogram").src = "/static/images/mel_spectrogram.png?t=" + new Date().getTime();
            document.getElementById("show-plots").style.display = "block";
        };
    }));
}

function stopRecording() {
    // Stop recording
    audioRecorder.stop();
    // Toggle buttons
    document.getElementById('stop').disabled = true;
    document.getElementById('start').removeAttribute('disabled');
    // Store recorded audio
    audioRecorder.getBuffers(gotBuffers);
}

function startRecording() {
    if (!audioRecorder)
        return;
    // Toggle buttons
    document.getElementById('start').disabled = true;
    document.getElementById('stop').removeAttribute('disabled');
    // Clear previous plots
    document.getElementById("show-plots").style.display = "none";
    // Start recording
    audioRecorder.clear();
    audioRecorder.record();
}

function gotStream(stream) {
    document.getElementById('start').removeAttribute('disabled');

    inputPoint = audioContext.createGain();

    // Create an audio node from the stream.
    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect(analyserNode);

    audioRecorder = new Recorder(inputPoint);

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect(zeroGain);
    zeroGain.connect(audioContext.destination);
}

function initAudio() {
    if (!navigator.getUserMedia)
        navigator.getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
    if (!navigator.cancelAnimationFrame)
        navigator.cancelAnimationFrame = navigator.webkitCancelAnimationFrame || navigator.mozCancelAnimationFrame;
    if (!navigator.requestAnimationFrame)
        navigator.requestAnimationFrame = navigator.webkitRequestAnimationFrame || navigator.mozRequestAnimationFrame;

    navigator.getUserMedia(
        {
            "audio": {
                "mandatory": {
                    "googEchoCancellation": "false",
                    "googAutoGainControl": "false",
                    "googNoiseSuppression": "false",
                    "googHighpassFilter": "false"
                },
                "optional": []
            },
        }, gotStream, function (e) {
            alert('Error getting audio');
            console.log(e);
        });
}

window.addEventListener('load', initAudio);

