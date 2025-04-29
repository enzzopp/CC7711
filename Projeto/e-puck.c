/*

 * File:          Controlador.c

 * Date:

 * Description:

 * Author:

 * Modifications:

 */

/*

 * You may need to add include files like <webots/distance_sensor.h> or

 * <webots/motor.h>, etc.

 */

#include <stdio.h>
#include <stdlib.h>
#include <webots/robot.h>

#include <webots/motor.h>

#include <webots/distance_sensor.h>

#include <webots/led.h>

/*

 * You may want to add macros here.

 */

#define TIME_STEP 256

#define QtddSensoresProx 8

#define QtddLeds 10

void parar_robo(WbDeviceTag MotorEsquerdo, WbDeviceTag MotorDireito)
{

    wb_motor_set_velocity(MotorEsquerdo, 0);

    wb_motor_set_velocity(MotorDireito, 0);
}

void andar_robo_frente(WbDeviceTag MotorEsquerdo, WbDeviceTag MotorDireito)
{

    wb_motor_set_velocity(MotorEsquerdo, 6.28);

    wb_motor_set_velocity(MotorDireito, 6.28);

    // andar pouco tempo (ajustável)
    for (int i = 0; i < 17; i++)
    {
        wb_robot_step(64);
    }
    parar_robo(MotorEsquerdo, MotorDireito);
}

void virar_robo_direita(WbDeviceTag MotorEsquerdo, WbDeviceTag MotorDireito)
{

    wb_motor_set_velocity(MotorEsquerdo, 6.28);

    wb_motor_set_velocity(MotorDireito, -6.28);

    // Aproximadamente 90 graus com essa velocidade (ajustável)
    for (int i = 0; i < 17; i++)
    {
        wb_robot_step(64);
    }

    parar_robo(MotorEsquerdo, MotorDireito);
}

void virar_robo_esquerda(WbDeviceTag MotorEsquerdo, WbDeviceTag MotorDireito)
{

    wb_motor_set_velocity(MotorEsquerdo, -6.28);

    wb_motor_set_velocity(MotorDireito, 6.28);

    // Aproximadamente 90 graus com essa velocidade (ajustável)
    for (int i = 0; i < 17; i++)
    {
        wb_robot_step(64);
    }

    parar_robo(MotorEsquerdo, MotorDireito);
}

int sortear_direcao()
{

    int direcao = rand() % 2;
    int direcao_sort = 0; // Variável para armazenar a direção sorteada

    if (direcao == 0)
    {
        direcao_sort = 1;
    }
    else
    {
        direcao_sort = 0;
    }

    return direcao_sort; // Retorna a direção sorteada (0 ou 1)
}

int main(int argc, char **argv)
{

    int i = 0;

    char texto[256];
    double Sensor_FrontalDireito;
    double Sensor_FrontalEsquerdo;

    double LeituraSensorProx[QtddSensoresProx];

    double AceleradorDireito = 1.0, AceleradorEsquerdo = 1.0;

    char *direcao_sort; // Variável para armazenar a direção sorteada

    /* necessary to initialize webots stuff */

    for (i = 0; i < 257; i++)
        texto[i] = '0';

    wb_robot_init();

    // configurei MOTORES

    WbDeviceTag MotorEsquerdo, MotorDireito;

    MotorEsquerdo = wb_robot_get_device("left wheel motor");

    MotorDireito = wb_robot_get_device("right wheel motor");

    wb_motor_set_position(MotorEsquerdo, INFINITY);

    wb_motor_set_position(MotorDireito, INFINITY);

    wb_motor_set_velocity(MotorEsquerdo, 0);

    wb_motor_set_velocity(MotorDireito, 0);

    // configurei Sensores de Proximidade

    WbDeviceTag SensorProx[QtddSensoresProx];

    SensorProx[0] = wb_robot_get_device("ps0");

    SensorProx[1] = wb_robot_get_device("ps1");

    SensorProx[2] = wb_robot_get_device("ps2");

    SensorProx[3] = wb_robot_get_device("ps3");

    SensorProx[4] = wb_robot_get_device("ps4");

    SensorProx[5] = wb_robot_get_device("ps5");

    SensorProx[6] = wb_robot_get_device("ps6");

    SensorProx[7] = wb_robot_get_device("ps7");

    wb_distance_sensor_enable(SensorProx[0], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[1], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[2], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[3], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[4], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[5], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[6], TIME_STEP);

    wb_distance_sensor_enable(SensorProx[7], TIME_STEP);

    // config leds

    WbDeviceTag Leds[QtddLeds];

    Leds[0] = wb_robot_get_device("led0");

    wb_led_set(Leds[0], -1);

    direcao_sort = sortear_direcao(); // Sorteia a direção inicial (0 ou 1)

    while (wb_robot_step(TIME_STEP) != -1)
    {

        for (i = 0; i < 256; i++)
            texto[i] = 0;

        Sensor_FrontalDireito = wb_distance_sensor_get_value(SensorProx[0]) - 60;
         sprintf(texto, "%s|%d: %5.2f  ", texto, 0, Sensor_FrontalDireito);

        Sensor_FrontalEsquerdo = wb_distance_sensor_get_value(SensorProx[7]) - 60;
         sprintf(texto, "%s|%d: %5.2f  ", texto, 7, Sensor_FrontalEsquerdo);

        if (Sensor_FrontalDireito >= 170 || Sensor_FrontalEsquerdo >= 170)
        {
            if (direcao_sort == 1)
            {
                parar_robo(MotorEsquerdo, MotorDireito);
                printf("Parar\n");
                virar_robo_direita(MotorEsquerdo, MotorDireito);
                andar_robo_frente(MotorEsquerdo, MotorDireito);
                printf("Virar\n");
                virar_robo_direita(MotorEsquerdo, MotorDireito);
                direcao_sort = 0;
            }
            else
            {
                parar_robo(MotorEsquerdo, MotorDireito);
                printf("Parar\n");
                virar_robo_esquerda(MotorEsquerdo, MotorDireito);
                andar_robo_frente(MotorEsquerdo, MotorDireito);
                printf("Virar\n");
                virar_robo_esquerda(MotorEsquerdo, MotorDireito);
                direcao_sort = 1;
            }
        }
        else
        {
            wb_motor_set_velocity(MotorEsquerdo, 6.28 * AceleradorEsquerdo);

            wb_motor_set_velocity(MotorDireito, 6.28 * AceleradorDireito);
        }

        /* Process sensor data here */

        /*for(i=0;i<QtddSensoresProx;i++){

           LeituraSensorProx[i]= wb_distance_sensor_get_value(SensorProx[i])-60;

           sprintf(texto,"%s|%d: %5.2f  ",texto,i,LeituraSensorProx[i]);

        }*/

        //  printf("%s\n", texto);

        wb_led_set(Leds[0], wb_led_get(Leds[0]) * -1);

        /*

         * Enter here functions to send actuator commands, like:

         * wb_motor_set_position(my_actuator, 10.0);

         */

        if (LeituraSensorProx[0] > 100)
        {

            AceleradorDireito = -1;

            AceleradorEsquerdo = 1;
        }

        else
        {

            AceleradorDireito = 1;

            AceleradorEsquerdo = 1;
        }
    };

    /* Enter your cleanup code here */

    /* This is necessary to cleanup webots resources */

    wb_robot_cleanup();

    return 0;
}