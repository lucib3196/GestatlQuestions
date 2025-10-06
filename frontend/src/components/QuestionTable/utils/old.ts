const handleRunTests = async () => {
        try {
            const ids = selected.map((s) => s.id);
            const res = await runQuestionTest(ids);
            setTestResults(res);
            toast.success("Ran Test Successfully");
        } catch (e) {
            console.error("Run tests failed", e);
        }
    };

    const handleDownload = async () => {
        try {
            const ids = selected.map((s) => s.id);
            await downloadQuestions(ids);
        } catch (error) {
            console.log(error);
        }
    };