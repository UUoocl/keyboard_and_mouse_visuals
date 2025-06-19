/*
----- Coding Tutorial by Patt Vira ----- 
Name: Sparkly Magic Wand
Video Tutorial: https://youtu.be/NW6fw_8s_0Y

Connect with Patt: @pattvira
https://www.pattvira.com/
----------------------------------------
*/

let stars = [];
let lastMouseX = 0, lastMouseY = 0
function setup() {
  createCanvas(windowWidth, windowHeight);
 }

function draw() {
  clear()
  background(0,0,0,0);
  if(mousePosX !== lastMouseX || mousePosY !== lastMouseY){
    stars.push(new Star(mousePosX, mousePosY, 0, 0, [255,255,0]));  
  }
  
  for (let i=stars.length-1; i>=0; i--) {
    stars[i].update();
    stars[i].display();
    
    if (stars[i].done) {
      stars.splice(i, 1);
    }
  }
  lastMouseX = mousePosX;
  lastMouseY = mousePosY;
 }

function mouseDragged() {
}

function mousePressed(mouseButton) {
  let num = random(20, 50);
  let fillColor = [255,0,255]
  if(mouseButton !== 'MB1'){fillColor = [129, 210, 235]}
  for (let i=0; i<num; i++) {
    let velocity = p5.Vector.random2D().mult(random(2, 5));
    stars.push(new Star(mousePosX, mousePosY, velocity.x, velocity.y,fillColor));
  }
}