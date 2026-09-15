%% Identyfikacja regulatorów PI — sekwencja skoków prędkości na obu burtach.
% Wymaga Instrument Control Toolbox (serialport). STM32 musi dostać "ready".
clear; clc; close all;

portName = "COM18";   % Linux: "/dev/ttyACM0"
baudRate = 115200;
maxTime = 15;         % czas całego eksperymentu [s]

try
    s = serialport(portName, baudRate);
    configureTerminator(s, "LF");  % STM32 kończy linię znakiem \n
    flush(s);
    disp("Connected to " + portName);
catch
    error("Could not open the serial port. Close any other terminal using it.");
end

dataMatrix = [];
startTime = tic;
isReadySent = false;
isSpeedSent1 = false;
isSpeedSent2 = false;
isSpeedSent3 = false;
isStopSent = false;

disp("Starting measurement sequence...");

while toc(startTime) < maxTime
    currentTime = toc(startTime);

    % --- Wysyłanie komend ---
    if ~isReadySent
        writeline(s, "ready");
        disp("[T=" + num2str(currentTime, "%.2f") + " s] sent: ready");
        isReadySent = true;
        pause(0.10);
    end

    if currentTime > 1 && ~isSpeedSent1
        writeline(s, "lspeed=20");
        writeline(s, "rspeed=20");
        disp("[T=" + num2str(currentTime, "%.2f") + " s] sent: lspeed=20, rspeed=20");
        isSpeedSent1 = true;
    end
    if currentTime > 5 && ~isSpeedSent2
        writeline(s, "lspeed=50");
        writeline(s, "rspeed=50");
        disp("[T=" + num2str(currentTime, "%.2f") + " s] sent: lspeed=50, rspeed=50");
        isSpeedSent2 = true;
    end
    if currentTime > 10 && ~isSpeedSent3
        writeline(s, "lspeed=-50");
        writeline(s, "rspeed=-50");
        disp("[T=" + num2str(currentTime, "%.2f") + " s] sent: lspeed=-50, rspeed=-50");
        isSpeedSent3 = true;
    end
    if currentTime > 13 && ~isStopSent
        writeline(s, "lspeed=0");
        writeline(s, "rspeed=0");
        disp("[T=" + num2str(currentTime, "%.2f") + " s] sent: stop");
        isStopSent = true;
    end

    % --- Odbiór telemetrii CSV (8 kolumn: zadanie/pomiar × 4 koła) ---
    if s.NumBytesAvailable > 0
        try
            lineStr = readline(s);
            values = str2double(split(lineStr, ","));
            if numel(values) >= 2 && all(~isnan(values(1:min(8, numel(values)))))
                dataMatrix = [dataMatrix; values(:)']; %#ok<AGROW>
            end
        catch
        end
    end
    pause(0.001);  % krótka pauza, żeby nie zablokować MATLABa i nie gubić bajtów
end

clear s;
disp("Measurement finished.");

if isempty(dataMatrix)
    warning("No telemetry received.");
    return;
end

samples = (1:size(dataMatrix, 1)) * 0.1;
titles = {
    "Right rear", "Right front", "Left rear", "Left front"
};
pairs = [1 2; 3 4; 5 6; 7 8];

for k = 1:size(pairs, 1)
    figure("Color", "w", "Name", titles{k});
    hold on;
    plot(samples, dataMatrix(:, pairs(k, 1)), "LineWidth", 1);
    plot(samples, dataMatrix(:, pairs(k, 2)), "LineWidth", 1.5);
    grid on;
    xlabel("Time [s]");
    ylabel("Speed [RPM]");
    legend("setpoint", "measured");
    title(titles{k});
    hold off;
end
