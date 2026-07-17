import { Empty, Panel, PanelTitle } from "../ui.jsx";

export default function Guide({ base, meta }) {
  if (!meta.guide)
    return (
      <Panel>
        <PanelTitle title="Study guide" />
        <Empty>
          No study guide in this pack yet.
          <br />
          <br />
          Generate one with the{" "}
          <span className="font-mono">course-study-guide</span> skill, then drop
          the PDF at{" "}
          <span className="font-mono">
            courses/{meta.slug}/study_guide.pdf
          </span>{" "}
          and refresh.
        </Empty>
      </Panel>
    );
  return (
    <Panel>
      <PanelTitle
        title="Study guide"
        sub="The exam-oriented reference built from the course source."
      />
      <div className="h-[78vh] overflow-hidden rounded-xl border border-line">
        <embed
          src={base + "/guide.pdf"}
          type="application/pdf"
          className="h-full w-full"
        />
      </div>
      <p className="mb-0 mt-2.5 text-[13px]">
        <a href={base + "/guide.pdf"} download className="text-crumb">
          Download PDF
        </a>
      </p>
    </Panel>
  );
}
