$(document).ready(function() {
    const selectedId = $('#subject-dropdown').val();
    let totalSeconds = 0;  // Keep track of total recording time

    $('#load-eeg-btn').click(function() {
        $.post('/init-eeg', { subject_id: selectedId }, function(response) {
            alert(response.message);
            totalSeconds = response.total_seconds;
            $('#eeg-slider').attr('max', totalSeconds - 15);
        }).fail(function(xhr) {
            alert('Error initializing EEG data');
        });
    });

    $('#eeg-slider').on('input change', function() {
        const startSecond = $(this).val();
        const windowLength = 15;  // Set this as desired
        $.get('/get-eeg-window', {
            start_second: startSecond,
            window_length: windowLength,
            canvas_width: $('#eeg-plot').width()
        }, function(data) {
            drawPlot(data);
        }).fail(function() {
            console.error('Error fetching EEG window');
        });
    });

    function drawPlot(data) {
        const trace = {
            y: data,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#17BECF' }
        };
        const layout = {
            // title: 'EEG Data Visualization',
            // xaxis: {
            //     title: 'Sample Index'
            // },
            // yaxis: {
            //     title: 'Voltage'
            // }
        };
        Plotly.newPlot('eeg-plot', [trace], layout);
    }
});
