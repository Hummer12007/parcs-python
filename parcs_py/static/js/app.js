$(document).ready(function () {
    $('.abort-job-btn').click(function (event) {
        var button = $(this);
        var jobId = button.data("job-id");
        $.ajax({
            url: '/api/job/'+ jobId,
            type: 'DELETE',
            success: function (result) {
                setTimeout(function () {
                    location.reload();
                }, 2000);
            },
            error: function (result) {
                alert('Unable to abort job.');
            }
        })
    });

    $('.remove-worker-btn').click(function (event) {
        var workerId = $(this).data('worker-id');
        $.ajax({
            url: '/api/worker/' + workerId,
            type: 'DELETE',
            success: function (result) {
                var workerElementId = '#' + 'worker-' + workerId + '-well';
                $(workerElementId).remove();
            },
            error: function (result) {
                alert('Unable to remove worker.');
            }
        });
    });


    $('.enable_disable-worker-btn').click(function (event) {
        var button = $(this);
        var worker_id = button.data('worker-id');
        var worker_element_id = '#' + 'worker-' + worker_id + '-well';
        var worker_well = $(worker_element_id);
        var state = button.attr('state');
        var opposite_state = 'enable';
        if (state === 'enable')
            opposite_state = 'disable';


        $.ajax({
            url: '/api/worker/' + worker_id + '/' + opposite_state,
            type: 'POST',
            success: function (result) {
                button.attr('state', opposite_state);
                if (opposite_state === 'disable') {
                    button.removeClass('btn-warning');
                    button.addClass('btn-success');
                    worker_well.addClass('disabled-worker');

                    button.text('Enable');

                } else {
                    button.addClass('btn-warning');
                    button.removeClass('btn-success');
                    worker_well.removeClass('disabled-worker');

                    button.text('Disable');
                }
            },
            error: function (result) {
                alert('Unable to change worker\'s state.');
            }
        });
    });

    $("#add-job-form").submit(function (event) {
        event.preventDefault();
        var data = new FormData();
        data.append('job_name', $('#job_name')[0].value);
        data.append('input_file', $('#input_file')[0].files[0]);
        data.append('solution_file', $('#solution_file')[0].files[0]);
        $.ajax({
            url: '/api/job',
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function (result) {
                window.location = '/jobs'
            },
            error: function (error) {
                alert('Wrong data!');
            }

        })
    });
});