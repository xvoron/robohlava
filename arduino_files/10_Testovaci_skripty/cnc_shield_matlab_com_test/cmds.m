%% MOVE X

cmd = 1;
mot = 1;
angle = 300; % 0 - 320

start_bit = 55;
stop_bit = 110;


payload = [cmd, mot, flip(typecast(uint16(angle), 'uint8'))];
msg = [start_bit, length(payload)+3, payload, stop_bit]
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% MOVE Y

cmd = 1;
mot = 2;
angle = 104; % 0 - 195

payload = [cmd, mot, flip(typecast(uint16(angle), 'uint8'))];
msg = [start_bit, length(payload)+3, payload, stop_bit]
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% READ X

cmd = 2;
mot = 1;

payload = [cmd, mot];
msg = [start_bit, length(payload)+3, payload, stop_bit];
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% READ Y

cmd = 2;
mot = 2;

payload = [cmd, mot];
msg = [start_bit, length(payload)+3, payload, stop_bit];
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% SET MOSFET

cmd = 3;
fet = 5; % 1 - 6
pwm = 0; % 0 - 255

payload = [cmd, fet, pwm];
msg = [start_bit, length(payload)+3, payload, stop_bit];
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% HOMING DONE

cmd = 4;

payload = [cmd];
msg = [start_bit, length(payload)+3, payload, stop_bit];
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'

%% HOMING 

cmd = 5;

payload = [cmd];
msg = [start_bit, length(payload)+3, payload, stop_bit]
fwrite(s, msg, "uint8");
fread(s, s.BytesAvailable, "uint8")'
