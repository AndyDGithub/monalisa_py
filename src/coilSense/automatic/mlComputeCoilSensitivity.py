from src.coilSense.nonCart.bmCoilSense_nonCart_secondary import bmCoilSense_nonCart_secondary
def mlComputeCoilSensitivity(BCreader, SCreader, CoilSensitivityFrameSize=[48, 48, 48], autoFlag=True, nIter=5):
    # ... (previous code remains unchanged)

    # Step 8: Refine coil sensitivities using iterative optimization
    C, _ = bmCoilSense_nonCart_secondary(y_surface, C_array_prime, y_ref, C_ref, Gn, Gu, Gut, ve, nIter, False)

    return C, mask
