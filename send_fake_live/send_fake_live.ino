void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  String a = (String)random(1, 1000);
  String b = (String)random(1, 1000);;
  String c = (String)random(1, 1000);;
  String d = (String)random(1, 1000);;
  String e = (String)random(1, 1000);;

  Serial.println(a + ',' + b + ',' + c + ',' + d + ',' + e);
}
