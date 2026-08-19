// Cross-code drag check: a submerged box towed at constant speed through still
// water, force read with Chrono::FSI-SPH's GetFsiBodyForce.
//
// Written for slot d19-priorcode, Can It Ford, 2026-08-19. The point is to get
// an INDEPENDENT implementation's number for the quantity our verdict chain
// rests on: horizontal hydrodynamic force on a bluff body at relative speed U.
//
// Design notes that matter for reading the output:
//   - U = 0 is a NO-FORCING CONTROL. Fx must come back ~0. If it does not, the
//     accessor or the setup is wrong and no other number here means anything.
//   - Motion is motor-prescribed (ChLinkMotorLinearSpeed), so this measures the
//     load on a body whose kinematics are imposed, exactly d17's configuration.
//   - Closed tank, so blockage and wall proximity are present and NOT corrected.
//     Reported Cd is therefore an apparent Cd, not a free-stream Cd.

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <cmath>

#include "chrono/physics/ChSystemNSC.h"
#include "chrono/physics/ChLinkMotorLinearSpeed.h"
#include "chrono/functions/ChFunctionConst.h"
#include "chrono_fsi/sph/ChFsiProblemSPH.h"

using namespace chrono;
using namespace chrono::fsi;
using namespace chrono::fsi::sph;

int main(int argc, char* argv[]) {
    // ---- parameters -------------------------------------------------------
    double U       = (argc > 1) ? std::atof(argv[1]) : 1.0;   // tow speed [m/s]
    double travel  = (argc > 2) ? std::atof(argv[2]) : 0.6;   // tow distance [m]
    double spacing = (argc > 3) ? std::atof(argv[3]) : 0.030; // SPH spacing [m]

    const ChVector3d fsize(1.6, 0.6, 0.5);      // channel L x W x depth [m]
    const ChVector3d bsize(0.20, 0.16, 0.16);   // towed box [m]
    const double rho = 1000.0;
    const double body_density = 2000.0;         // heavy; motor carries it anyway
    const double step_size = 1e-4;

    // t_end from travel; U = 0 still needs a finite window for the control.
    double t_end = (U > 1e-9) ? (travel / U) : 0.5;

    ChSystemNSC sysMBS;
    sysMBS.SetCollisionSystemType(ChCollisionSystem::Type::BULLET);

    ChFsiProblemCartesian fsi(spacing, &sysMBS);
    fsi.SetVerbose(false);
    fsi.SetGravitationalAcceleration(ChVector3d(0, 0, -9.81));
    fsi.SetStepSizeCFD(step_size);
    fsi.SetStepsizeMBD(step_size);

    ChFsiFluidSystemSPH::FluidProperties fluid_props;
    fluid_props.density   = rho;
    fluid_props.viscosity = 1e-3;               // water
    fsi.SetCfdSPH(fluid_props);

    ChFsiFluidSystemSPH::SPHParameters sph_params;
    sph_params.integration_scheme  = IntegrationScheme::RK2;
    sph_params.num_bce_layers      = 4;
    sph_params.initial_spacing     = spacing;
    sph_params.d0_multiplier       = 1;
    sph_params.max_velocity        = 5.0;
    sph_params.shifting_method     = ShiftingMethod::XSPH;
    sph_params.shifting_xsph_eps   = 0.5;
    sph_params.artificial_viscosity = 0.03;
    sph_params.eos_type            = EosType::TAIT;
    sph_params.num_proximity_search_steps = 1;
    sph_params.use_delta_sph        = true;
    sph_params.delta_sph_coefficient = 0.1;
    sph_params.use_variable_time_step = false;
    sph_params.boundary_method     = BoundaryMethod::ADAMI;
    sph_params.viscosity_method    = ViscosityMethod::ARTIFICIAL_UNILATERAL;
    fsi.SetSPHParameters(sph_params);

    // ---- towed body -------------------------------------------------------
    ChBox box(bsize);
    double mass = body_density * box.GetVolume();
    ChMatrix33d inertia = mass * box.GetGyration();

    auto geometry = chrono_types::make_shared<utils::ChBodyGeometry>();
    geometry->materials.push_back(ChContactMaterialData());
    geometry->coll_boxes.push_back(utils::ChBodyGeometry::BoxShape(VNULL, QUNIT, box));

    // Start upstream of centre, fully submerged at mid-depth.
    double x0 = -0.5;
    double z0 = 0.25;
    auto body = chrono_types::make_shared<ChBody>();
    body->SetName("towed_box");
    body->SetPos(ChVector3d(x0, 0, z0));
    body->SetRot(QUNIT);
    body->SetMass(mass);
    body->SetInertia(inertia);
    body->SetFixed(true);   // kinematics prescribed by hand, no motor constraint
    body->EnableCollision(false);
    sysMBS.AddBody(body);
    fsi.AddRigidBody(body, geometry, true, true);

    // No ChLinkMotorLinearSpeed. The first two attempts used one and the body
    // pose went NaN on the very first step, poisoning its BCE markers. Motion is
    // now imposed directly on a fixed body, which is also how our own driver
    // prescribes the vehicle, so the comparison is closer, not further away.

    // Depth-based initial pressure. Omitting this starts the whole column at
    // p = 0, which collapses under gravity and NaNs the run; that is exactly
    // what happened on the first attempt and it is recorded rather than hidden.
    fsi.RegisterParticlePropertiesCallback(
        chrono_types::make_shared<DepthPressurePropertiesCallback>(fsize.z()));

    fsi.Construct(fsize, ChVector3d(0, 0, 0), BoxSide::ALL & ~BoxSide::Z_POS);
    fsi.Initialize();

    // ---- run --------------------------------------------------------------
    const double meta = 10 * step_size;
    double t = 0;
    std::printf("# chrono_tow_drag  U=%.4f  travel=%.3f  spacing=%.4f  t_end=%.4f\n",
                U, travel, spacing, t_end);
    std::printf("# box=%.3fx%.3fx%.3f  A_ref=%.5f m2  rho=%.1f\n",
                bsize.x(), bsize.y(), bsize.z(), bsize.y() * bsize.z(), rho);
    std::printf("t_s,x_m,vx_ms,Fx_N,Fy_N,Fz_N\n");

    // Settle with the motor holding the body at rest. The mean Fx over this
    // window is a built-in no-forcing control for every run, not just U = 0.
    const double t_settle = 0.25;
    std::vector<double> fx_settle;
    while (t < t_settle) {
        body->SetPos(ChVector3d(x0, 0, z0));
        body->SetPosDt(VNULL);
        fsi.DoStepDynamics(meta);
        t += meta;
        auto F = fsi.GetFsiBodyForce(body);
        auto p = body->GetPos();
        auto v = body->GetPosDt();
        std::printf("%.5f,%.5f,%.5f,%.6f,%.6f,%.6f\n", t, p.x(), v.x(), F.x(), F.y(), F.z());
        fx_settle.push_back(F.x());
    }
    double s_sum = 0;
    for (size_t i = fx_settle.size() / 2; i < fx_settle.size(); ++i) s_sum += fx_settle[i];
    double settle_mean = fx_settle.empty() ? 0.0 : s_sum / (fx_settle.size() - fx_settle.size() / 2);

    // tow begins here
    double t_tow_end = t + t_end;

    std::vector<double> fx_hist, t_hist;
    double x_cur = x0;
    while (t < t_tow_end) {
        // Impose pose and velocity BEFORE the step so the BCE markers carry the
        // right wall velocity for this step, not the previous one.
        x_cur += U * meta;
        body->SetPos(ChVector3d(x_cur, 0, z0));
        body->SetPosDt(ChVector3d(U, 0, 0));
        fsi.DoStepDynamics(meta);
        t += meta;
        auto F = fsi.GetFsiBodyForce(body);
        auto p = body->GetPos();
        auto v = body->GetPosDt();
        std::printf("%.5f,%.5f,%.5f,%.6f,%.6f,%.6f\n",
                    t, p.x(), v.x(), F.x(), F.y(), F.z());
        t_hist.push_back(t);
        fx_hist.push_back(F.x());
    }

    // Steady window = last 50 percent of the record, stated explicitly so the
    // number is reproducible rather than eyeballed.
    size_t n = fx_hist.size();
    size_t i0 = n / 2;
    double sum = 0, sum2 = 0;
    for (size_t i = i0; i < n; ++i) { sum += fx_hist[i]; sum2 += fx_hist[i] * fx_hist[i]; }
    size_t m = n - i0;
    double mean = (m > 0) ? sum / m : 0.0;
    double var  = (m > 1) ? (sum2 / m - mean * mean) : 0.0;
    double sd   = (var > 0) ? std::sqrt(var) : 0.0;
    double A    = bsize.y() * bsize.z();
    double Cd   = (U > 1e-9) ? (2.0 * mean / (rho * A * U * U)) : NAN;

    std::printf("# SETTLE_CONTROL U=%.4f meanFx_settle=%.6f N (motor held at rest, expect ~0)\n",
                U, settle_mean);
    std::printf("# SUMMARY U=%.4f n=%zu window=last%zu meanFx=%.6f N sdFx=%.6f N Cd_apparent=%.6f\n",
                U, n, m, mean, sd, Cd);
    return 0;
}
