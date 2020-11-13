clc, clear;

s = serial('COM67','BaudRate', 115200);
fopen(s);

start_bit = 55;
stop_bit = 110;


%%
fclose(s);