$(document).ready(function() {
        // Load subjects dynamically
        $.ajax({
            url: '/list-subjects',  // Ensure this route is defined in your Flask app
            type: 'GET',
            success: function(data) {
                data.forEach(function(subject) {
                    $('#subject-dropdown').append($('<option></option>').val(subject.id).html(subject.id));
                });
            },
            error: function() {
                console.log('Error loading subjects');
            }
        });

        // Fetch details for the selected subject
        $('#subject-dropdown').change(function() {
            var selectedId = $(this).val();
            if (!selectedId) {
                $('#last-recording-time').text('N/A');
                $('#battery-status').text('N/A');
                return;
            }
            $.ajax({
                url: '/get-subject-info/' + selectedId,  // Ensure this route is defined in your Flask app
                type: 'GET',
                success: function(data) {
                    $('#last-recording-time').text(data.last_recorded_time);
                    $('#battery-status').text(data.battery_status);
                },
                error: function(response) {
                    alert('Error: ' + response.responseText);
                }
            });
        });
    });