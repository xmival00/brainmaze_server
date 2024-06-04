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
                if (data.length > 0) {
                    if (!table) { // Initialize DataTable only if it hasn't been initialized before
                        var columns = Object.keys(data[0]).map(function(key) {
                            return { title: key, data: key };
                        });
                        table = $('#data-table').DataTable({
                            data: data,
                            columns: columns,
                            destroy: true,
                            retrieve: true,
                            // ordering: false,

                        });
                    } else {
                        table.clear(); // Clear existing data
                        table.rows.add(data); // Add new data
                        table.draw(); // Redraw the table
                    }
                } else {
                    if (table) {
                        table.clear().draw();
                    }
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
            $('#eeg-slider').attr('max', totalSeconds - 15);
            $('#eeg-slider').val(1).trigger('change');
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

});
