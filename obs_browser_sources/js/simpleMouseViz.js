let mousePosX = 0, mousePosY =0;
function setup() {
    createCanvas(windowWidth, windowHeight);
    noStroke();
    rectMode(CENTER);
  }
  
  function draw() {
    clear()
    background(0,0,0,0);
    strokeWeight(8)
    stroke(55)
    fill(172, 112, 240,255);
    rect(mousePosX, mousePosY, 500, 500); 
  }