class Control_function_DTO:
    def __init__(self, type_of_search, type_of_coverage, type_of_exploration, expl_weight, is_concurrent):
        self.type_of_search = type_of_search
        self.type_of_coverage = type_of_coverage
        self.type_of_exploration = type_of_exploration
        self.expl_weight = expl_weight
        self.is_concurrent = is_concurrent