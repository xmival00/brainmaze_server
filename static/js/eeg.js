$(document).ready(function() {
    const selectedId = $('#subject-dropdown').val();
    let totalSeconds = 0;  // Keep track of total recording time

    // $('#load-eeg-btn').click(function() {
    //     $.post('/init-eeg', { subject_id: selectedId }, function(response) {
    //         alert(response.message);
    //         totalSeconds = response.total_seconds;
    //         $('#eeg-slider').attr('max', totalSeconds - 15);
    //     }).fail(function(xhr) {
    //         alert('Error initializing EEG data');
    //     });
    // });

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
        const trace_window1 = {
            x: data.time_data,
            y: data.data[0],  // Assuming data is a list of lists or similar structure
            xaxis: 'x1',
            yaxis: 'y1',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#000000' }
        };

        const trace_window2 = {
            x: data.time_data,
            y: data.data[1],  // Second dataset for the subplot
            xaxis: 'x2',
            yaxis: 'y2',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#000000' }
        };

        const trace_recording1 = {
            x: data.recording_time,
            y: data.recording_trace[0],  // Assuming data is a list of lists or similar structure
            xaxis: 'x3',
            yaxis: 'y3',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#868686' }
         };
         const trace_recording2 = {
                x: data.recording_time,
                y: data.recording_trace[1],  // Assuming data is a list of lists or similar structure
                xaxis: 'x4',
                yaxis: 'y4',
                type: 'scatter',
                mode: 'lines',
                line: { color: '#868686' }
        };

        const layout = {
            grid: {rows: 4, columns: 1, pattern: 'independent'},
            margin: {
                l: 40,  // Left margin
                r: 40,  // Right margin
                b: 40,  // Bottom margin (reduce to bring x-labels closer)
                t: 60,  // Top margin (reduce to bring title closer)
                pad: 4
            },
            shapes: [
                {
                    type: 'rect',
                    xref: 'x3',
                    yref: 'y3',  // Span the rectangle the full height of the plotting area
                    x0: data.start_window,
                    x1: data.end_window,
                    y0: data.range_trace[0][0],
                    y1: data.range_trace[0][1],
                    fillcolor: 'Red',
                    opacity: 0.5,
                    line: {
                        width: 1
                    }
                },
                {
                    type: 'rect',
                    xref: 'x4',
                    yref: 'y4',  // Span the rectangle the full height of the plotting area
                    x0: data.start_window,
                    x1: data.end_window,
                    y0: data.range_trace[1][0],
                    y1: data.range_trace[1][1],
                    fillcolor: 'Red',
                    opacity: 0.5,
                    line: {
                        width: 1
                }
                }
            ],
        xaxis1: {
            title: '', // No title for the x-axis of the top plots
            domain: [0, 1],
            anchor: 'y1',
            showticklabels: false,
        },
        yaxis1: {
            title: data.ch_names[0],
            domain: [0.8, 1], // Top-most plot
            anchor: 'x1',
            range: data.range_trace[0],
        },
        xaxis2: {
            title: 'Time',
            domain: [0, 1],
            anchor: 'y2',
        },
        yaxis2: {
            title: data.ch_names[1],
            domain: [0.6, 0.8], // Second plot from the top
            anchor: 'x2',
            range: data.range_trace[1],
        },
        xaxis3: {
            title: '',
            domain: [0, 1],
            anchor: 'y3',
            showticklabels: false
        },
        yaxis3: {
            title: data.ch_names[0],
            domain: [0.2, 0.4], // Third plot from the top
            range: data.range_trace[0],
            anchor: 'x3',
        },
        xaxis4: {
            title: 'Time (minutes)',
            domain: [0, 1],
            anchor: 'y4'
        },
        yaxis4: {
            title: data.ch_names[1],
            domain: [0, 0.2], // Bottom-most plot
            range: data.range_trace[1],
            anchor: 'x4',
        },
        };

        const config = {
            displayModeBar: false, // Disable the mode bar entirely
            // staticPlot: true
        };

        Plotly.newPlot('eeg-plot', [trace_recording1, trace_recording2, trace_window1, trace_window2], layout, config);
    }

});
