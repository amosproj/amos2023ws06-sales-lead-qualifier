# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

from bdc.steps.enrich_custom_domains import EnrichCustomDomains


class Pipeline:
    def __init__(self, steps):
        self.steps = steps

    def run(self):
        for step in self.steps:
            step.load_data()
            if step.verify():
                step.run()
            step.finish()


if __name__ == "__main__":
    enrich_domain_step = EnrichCustomDomains()
    pipeline = Pipeline([enrich_domain_step])
    pipeline.run()
