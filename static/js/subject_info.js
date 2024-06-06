$(document).ready(function() {
    // Variable to store DataTable instance
    var table = null;

    // Load subjects dynamically
    $.ajax({
        url: '/list-subjects',
        type: 'GET',
        success: function(data) {
            data.forEach(function(subject) {
                $('#subject-dropdown').append($('<option></option>').val(subject).html(subject));
            });
        },
        error: function() {
            console.log('Error loading subjects');
        }
    });


    $('#subject-dropdown').change(function() {
        var selectedId = $(this).val();
        if (!selectedId) {
            if (table) {
                table.clear().draw();
            }
            return;
        }
        $.ajax({
            url: '/get-subject-info/' + selectedId,
            type: 'GET',
            success: function(data) {
                
                if (data.data.length > 0) {
                    if (!table) { // Initialize DataTable only if it hasn't been initialized before
                        var columns = Object.keys(data.data[0]).map(function(key) {
                            return { title: key, data: key };
                        });
                        table = $('#data-table').DataTable({
                            data: data.data,
                            columns: columns,
                            destroy: true,
                            retrieve: true,
                            // ordering: false,

                        });
                    } else {
                        table.clear(); // Clear existing data
                        table.rows.add(data.data); // Add new data
                        table.draw(); // Redraw the table
                    }
                } else {
                    if (table) {
                        table.clear().draw();
                    }
                }

                const intervals = JSON.parse(data.intervals);
                if (intervals.length > 0) {
                    drawOverview(intervals, data.start, data.stop);
                }
            },
            error: function() {
                console.error('Error loading data');
                if (table) {
                    table.clear().draw();
                }
            }
        });
    });
    

    // Event listener for selecting a row
    $('#data-table tbody').on('click', 'tr', function () {
        $('#loading').removeClass('invisible');
        $('#loading strong').text('Loading data...');
        var data = table.row(this).data();
        var pathRaw = data['path_raw']; // Ensure this key matches the column in your data

        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            table.$('tr.selected').removeClass('selected');  // Deselect all other rows
            $(this).addClass('selected');  // Select this row
        }

        $.post('/init-eeg', { file_path: pathRaw }, function(response) {
            alert(response.message);
            totalSeconds = response.total_seconds;
            $('#eeg-slider').removeClass('invisible');
            $('#eeg-slider').attr('max', totalSeconds - 15);
            $('#eeg-slider').val(1).trigger('change');
            $('#loading strong').text('Constructing graph...');
        }).fail(function(xhr) {
            alert('Error initializing EEG data');
        });
    });


    // $('#load-eeg-btn').click(function() {
    //     $.post('/init-eeg', { subject_id: selectedId }, function(response) {
    //         alert(response.message);
    //         totalSeconds = response.total_seconds;
    //         $('#eeg-slider').attr('max', totalSeconds - 15);
    //     }).fail(function(xhr) {
    //         alert('Error initializing EEG data');
    //     });
    // });


    function drawOverview(intervals, start, stop){
        console.log(intervals);

        // Step 1: Extract unique classes
        const uniqueClasses = [...new Set(intervals.map(interval => interval.class))];
        uniqueClasses.sort((a, b) => {
            const aNum = parseInt(a.split('-')[0]);
            const bNum = parseInt(b.split('-')[0]);
            return aNum - bNum;
        });
        console.log(uniqueClasses);

        // Step 2: Define a function to generate unique colors
        function generateColor(classIndex) {
            const hue = classIndex * (360 / uniqueClasses.length);
            return `hsl(${hue}, 70%, 50%)`; // Use HSL color space for better differentiation
        }

        // Step 3: Map each class to its corresponding color
        const classColors = {};
        uniqueClasses.forEach((className, index) => {
            classColors[className] = generateColor(index);
        });

        // Construct traces
        const traces = intervals.map(interval => ({
            type: 'scatter',
            x: [interval.range0, interval.range1],
            y: [interval.class, interval.class],
            mode: 'lines',
            name: interval.class,
            line: { color: classColors[interval.class] }
        }));

        // Define layout
        var layout = {
            title: 'Channel Active',
            xaxis: {
                title: 'Time',
                // autorange: true,
                range: [start, stop],
            },
            yaxis: {
                title: 'Channel',
                categoryorder: 'array',
                categoryarray: uniqueClasses
            },
            showlegend: false  // Turn off legend
        };

        // Plot the chart with layout
        Plotly.newPlot('overview', traces, layout);
    }

});
