/* Fixture-limited CPU linear-blend skinning. No vertex frames stored. */
#include "skin_data.h"
static void lab_skin_evaluate(int frame, float result[10][3]) {
    int v, axis, influence, k;
    frame %= 165;
    for (v=0;v<10;v++) for(axis=0;axis<3;axis++) {
        float sum=0.0f;
        for(influence=0;influence<4;influence++) {
            int joint=lab_skin_joints[v][influence];
            float w=lab_skin_weights[v][influence];
            const float *row=lab_skin_matrices[frame][joint][axis];
            float p=row[3];
            for(k=0;k<3;k++) p+=row[k]*lab_skin_positions[v][k];
            sum+=w*p;
        }
        result[v][axis]=180.0f*sum;
    }
}
