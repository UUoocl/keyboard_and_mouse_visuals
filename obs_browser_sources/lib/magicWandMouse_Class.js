class Star {
  constructor(x, y, vx, vy, fillColor) {
    this.position = createVector(x, y);
    this.velocity = createVector(vx, vy);
    this.acceleration = createVector(0, 0);
    this.fillColor = fillColor

    this.rot = random(TWO_PI);
    this.size = random(1, 10);
    
    this.life = 255;
    this.done = false;
    
    this.rand = random() > 0.5;
  }
  
  update() {
    this.finished();
    this.life -= 5;
    
    if (this.rand) {
      this.acceleration = p5.Vector.random2D().mult(0.05);
    }
    
    this.velocity.add(this.acceleration);
    this.position.add(this.velocity);
  }
  
  display() {

    fill(this.fillColor[0],this.fillColor[1],this.fillColor[2], this.life);
    push();
    translate(this.position.x, this.position.y);
    rotate(this.rot);

    drawingContext.shadowOffsetX = 5;
    drawingContext.shadowOffsetY = -5;
    drawingContext.shadowBlur = 10;
    drawingContext.shadowColor = color(0, 0, 0,50);

    noStroke();
    beginShape();
    vertex(0, -this.size);
    quadraticVertex(0, 0, this.size, 0);
    quadraticVertex(0, 0, 0, this.size);
    quadraticVertex(0, 0, -this.size, 0);
    quadraticVertex(0, 0, 0, -this.size);
    endShape(CLOSE);
    pop();
  }
  
  finished() {
    if (this.life < 0) {
      this.done = true;
    }
  }
}