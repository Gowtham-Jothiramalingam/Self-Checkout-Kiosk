
#include "ESP_MICRO.h" //Include the micro library 
int testvariable = 0;
void setup(){
  Serial.begin(9600); // Starting serial port for seeing details
  start("Gowtham","012345678");  // EnAIt will connect to your wifi with given details
}
void loop(){
  waitUntilNewReq();  //Waits until a new request from python come
  /* increases index when a new request came*/
  testvariable += 1;
  returnThisInt(testvariable); //Returns the data to python
}
