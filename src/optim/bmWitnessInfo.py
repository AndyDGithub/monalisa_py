class bmWitnessInfo:
    def __init__(self, *args):
        # if args[0] is instance of bmWitnessInfo: copy
        if args and isinstance(args[0], bmWitnessInfo):
            in_witnessInfo = args[0]
            self.save_witnessIm_flag = in_witnessInfo.save_witnessIm_flag
            self.witness_name = in_witnessInfo.witness_name
            self.witness_ind = in_witnessInfo.witness_ind
            self.witness_im = in_witnessInfo.witness_im
            self.witness_time = in_witnessInfo.witness_time
            self.creationTime = in_witnessInfo.creationTime
            self.finalCallTime = in_witnessInfo.finalCallTime
            self.finalInd = in_witnessInfo.finalInd
            self.param = in_witnessInfo.param
            self.param_name = in_witnessInfo.param_name
        else:
            # handle arguments
            witness_name = None
            witness_ind = None
            save_witnessIm_flag = False
            if len(args) > 0:
                witness_name = args[0]
            if len(args) > 1:
                witness_ind = args[1]
            if len(args) > 2:
                save_witnessIm_flag = args[2]
            self.witness_name = witness_name
            self.witness_ind = witness_ind if witness_ind is not None else []
            self.save_witnessIm_flag = save_witnessIm_flag
            self.witness_im = []
            self.witness_time = []
            self.creationTime = None
            self.finalCallTime = None
            self.finalInd = None
            self.param = None
            self.param_name = None
