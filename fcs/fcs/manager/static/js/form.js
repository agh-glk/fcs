$(function() {
  $(':input').each(function() {
    $(this).addClass('form-control');
    $(this).attr('placeholder',$(this).attr('name'));
  });
});