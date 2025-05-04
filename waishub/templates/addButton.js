document.addEventListener('DOMContentLoaded', function() {
    const plusIcon = document.getElementById('plus-icon');
    const plusMenu = document.getElementById('plus-menu');
  
    plusIcon.addEventListener('click', function() {
      plusMenu.classList.toggle('show');
    });
  });