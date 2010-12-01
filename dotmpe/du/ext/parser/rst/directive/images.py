from docutils.parsers.rst.directives import images


class Figure(images.Figure):

    option_spec['label'] = directives.unchanged

    # XXX: override for 'label'
    def run(self):
        figwidth = self.options.pop('figwidth', None)
        figclasses = self.options.pop('figclass', None)
        align = self.options.pop('align', None)
        label = self.options.pop('label', None)
        (image_node,) = Image.run(self)
        if isinstance(image_node, nodes.system_message):
            return [image_node]
        figure_node = nodes.figure('', image_node)
        if figwidth == 'image':
            if PIL and self.state.document.settings.file_insertion_enabled:
                # PIL doesn't like Unicode paths:
                try:
                    i = PIL.open(str(image_node['uri']))
                except (IOError, UnicodeError):
                    pass
                else:
                    self.state.document.settings.record_dependencies.add(
                        image_node['uri'])
                    figure_node['width'] = i.size[0]
        elif figwidth is not None:
            figure_node['width'] = figwidth
        if figclasses:
            figure_node['classes'] += figclasses
        if align:
            figure_node['align'] = align
        figure_node['label'] = label
        if self.content:
            node = nodes.Element()          # anonymous container for parsing
            self.state.nested_parse(self.content, self.content_offset, node)
            first_node = node[0]
            if isinstance(first_node, nodes.paragraph):
                caption = nodes.caption(first_node.rawsource, '',
                                        *first_node.children)
                figure_node += caption
            elif not (isinstance(first_node, nodes.comment)
                      and len(first_node) == 0):
                error = self.state_machine.reporter.error(
                      'Figure caption must be a paragraph or empty comment.',
                      nodes.literal_block(self.block_text, self.block_text),
                      line=self.lineno)
                return [figure_node, error]
            if len(node) > 1:
                figure_node += nodes.legend('', *node[1:])
        return [figure_node]

