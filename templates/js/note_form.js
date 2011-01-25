function calcElapsedTime(year1, month1, day1, hour1, minute1, year2, month2, day2, hour2, minute2) {
  var dt1 = new Date(year1, month1 - 1, day1, hour1, minute1);
  var dt2 = new Date(year2, month2 - 1, day2, hour2, minute2);
  var diff = dt2 - dt1;
  var diffMinute = diff / 60000;//1分は60000ミリ秒
  return diffMinute;
}

$(function(){

  // 初期化処理
  if ($('#id_elapsed_time_0').val() == '') {
    $('#id_elapsed_time_0').val('0');
    $('#id_elapsed_time_1').val('0');
    $('#auto_calc').attr('checked', true)
  }

  var date_nodes = [
      '#id_start_0_year', '#id_start_0_month', '#id_start_0_day',
       '#id_start_1_hour', '#id_start_1_minute',
       '#id_end_0_year', '#id_end_0_month', '#id_end_0_day',
       '#id_end_1_hour', '#id_end_1_minute'
  ];
  
  for (var i = 0; i < date_nodes.length; i++) {
    $(date_nodes[i])
      .change(function(){
        if ($('#auto_calc').attr('checked')) {
          var elapsed_time = calcElapsedTime(
                      $(date_nodes[0]).val(),
                      $(date_nodes[1]).val(),
                      $(date_nodes[2]).val(),
                      $(date_nodes[3]).val(),
                      $(date_nodes[4]).val(),
                      $(date_nodes[5]).val(),
                      $(date_nodes[6]).val(),
                      $(date_nodes[7]).val(),
                      $(date_nodes[8]).val(),
                      $(date_nodes[9]).val()
                    );
          var hour = Math.floor(elapsed_time / 60);
          var minute = elapsed_time % 60;
          $('#id_elapsed_time_0').val(hour);
          $('#id_elapsed_time_1').val(minute);
        }
      });
  }
});

