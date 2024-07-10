// document.addEventListener('DOMContentLoaded', function() {
  // alert('clothing_size.js loaded');
  let cmRadio = null;
  let inchesRadio = null
  let cmTable = null
  let inchesTable = null
  let labelCm = null
  let labelInches = null

  if(document.getElementById('cm')){
    cmRadio = document.getElementById('cm');
  }

  if(document.getElementById('inches')){
    inchesRadio = document.getElementById('inches');
  }
  if(document.getElementById('cmTable')){
    cmTable = document.getElementById('cmTable');
  }
  
  if(document.getElementById('inchesTable')){
    inchesTable = document.getElementById('inchesTable');
  }
  if(document.getElementById('label-cm')){
    labelCm = document.getElementById('label-cm');
  }
  if(document.getElementById('label-inches')){
    labelInches = document.getElementById('label-inches');
  }

if(cmRadio){
  cmRadio.addEventListener('change', function() {
    if (cmRadio.checked) {
      cmTable.style.display = 'table';
      inchesTable.style.display = 'none';
      labelCm.classList.add('active');
      labelInches.classList.remove('active');
    }
  });

}
  
if(inchesRadio){
  inchesRadio.addEventListener('change', function() {
    if (inchesRadio.checked) {
      cmTable.style.display = 'none';
      inchesTable.style.display = 'table';
      labelCm.classList.remove('active');
      labelInches.classList.add('active');
    }
  });
}

if(cmRadio){
  // Initialize display
  if (cmRadio.checked) {
    cmTable.style.display = 'table';
    inchesTable.style.display = 'none';
    labelCm.classList.add('active');
    labelInches.classList.remove('active');
  } else {
    cmTable.style.display = 'none';
    inchesTable.style.display = 'table';
    labelCm.classList.remove('active');
    labelInches.classList.add('active');
  }
}
  
