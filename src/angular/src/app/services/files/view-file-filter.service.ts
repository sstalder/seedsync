import {Injectable} from "@angular/core";
import {Observable} from "rxjs/Observable";
import {BehaviorSubject} from "rxjs/Rx";

import * as Immutable from "immutable";

import {LoggerService} from "../utils/logger.service";
import {ViewFile} from "./view-file";
import {ViewFileFilterCriteria, ViewFileService} from "./view-file.service";
import {ViewFileFilter} from "./view-file-filter";


class AndFilterCriteria implements ViewFileFilterCriteria {
    constructor(private a: ViewFileFilterCriteria,
                private b: ViewFileFilterCriteria) {
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        return this.a.meetsCriteria(viewFile) && this.b.meetsCriteria(viewFile);
    }
}

class StatusFilterCriteria implements ViewFileFilterCriteria {
    status: ViewFile.Status = null;

    meetsCriteria(viewFile: ViewFile): boolean {
        return this.status == null || this.status === viewFile.status;
    }
}

class NameFilterCriteria implements ViewFileFilterCriteria {
    private _name: string = null;
    private _queryCandidates = [];

    get name(): string {
        return this._name;
    }

    set name(name: string) {
        this._name = name;
        const query = this._name.toLowerCase();
        this._queryCandidates = [
            query,
            query.replace(/\s/g, "."),
        ];
    }

    meetsCriteria(viewFile: ViewFile): boolean {
        if (this._name == null || this._name === "") { return true; }
        const search = viewFile.name.toLowerCase();
        return this._queryCandidates.reduce(
            (a: boolean, b: string) => a || search.indexOf(b) >= 0,
            false  // initial value
        );
    }
}


/**
 * ViewFileFilterService class provides filtering services for
 * view files
 *
 * This class provides actions to control the filtering parameters.
 * It also provides the filter state for display purposes.
 */
@Injectable()
export class ViewFileFilterService {

    private _filter: BehaviorSubject<ViewFileFilter> = new BehaviorSubject(new ViewFileFilter({}));

    private _viewFiles: Immutable.List<ViewFile> = Immutable.List<ViewFile>([]);
    private _statusFilter: StatusFilterCriteria = new StatusFilterCriteria();
    private _nameFilter: NameFilterCriteria = new NameFilterCriteria();

    constructor(private _logger: LoggerService,
                private _viewFileService: ViewFileService) {
        _viewFileService.files.subscribe(files => {
            this._viewFiles = files;
            this.updateState();
        });

        // Setup the filters
        this._viewFileService.setFilterCriteria(new AndFilterCriteria(this._statusFilter, this._nameFilter));
    }

    get filter(): Observable<ViewFileFilter> {
        return this._filter.asObservable();
    }

    /**
     * Filter by status
     * @param {ViewFile.Status} status, or null for disabled/all
     */
    public filterStatus(status: ViewFile.Status) {
        if (this._statusFilter.status === status) { return; }

        if (this.isStatusEnabled(status)) {
            this._logger.debug("Setting status filter: %O", status == null ? "all" : status);
            this._statusFilter.status = status;
            // Note: updateState() will be called when filters are reapplied
            //       but we call it anyways to speed up the UI update of filter state
            this.updateState();
            this._viewFileService.reapplyFilters();
        } else {
            // Normally we would want to log a warning here, however the component
            // currently has no way to disable the click action on a button because
            // async pipes cannot be used inside the click action. Therefore, the
            // component has no way to disable the button on its end
            // So instead, we gracefully accept this invalid action and do nothing
        }
    }

    /**
     * Filter by name
     * @param {string} name
     */
    public filterName(name: string) {
        if (this._nameFilter.name === name) { return; }

        this._nameFilter.name = name;
        this._viewFileService.reapplyFilters();
    }

    private isStatusEnabled(status: ViewFile.Status) {
        if (status == null) { return true; }
        return this._viewFiles.findIndex(f => f.status === status) >= 0;
    }

    private updateState() {
        const extractedEn = this.isStatusEnabled(ViewFile.Status.EXTRACTED);
        const extractingEn = this.isStatusEnabled(ViewFile.Status.EXTRACTING);
        const downloadedEn = this.isStatusEnabled(ViewFile.Status.DOWNLOADED);
        const downloadingEn = this.isStatusEnabled(ViewFile.Status.DOWNLOADING);
        const queuedEn = this.isStatusEnabled(ViewFile.Status.QUEUED);
        const stoppedEn = this.isStatusEnabled(ViewFile.Status.STOPPED);
        const defaultEn = this.isStatusEnabled(ViewFile.Status.DEFAULT);

        const allSel = this._statusFilter.status == null;
        const extractedSel = this._statusFilter.status === ViewFile.Status.EXTRACTED;
        const extractingSel = this._statusFilter.status === ViewFile.Status.EXTRACTING;
        const downloadedSel = this._statusFilter.status === ViewFile.Status.DOWNLOADED;
        const downloadingSel = this._statusFilter.status === ViewFile.Status.DOWNLOADING;
        const queuedSel = this._statusFilter.status === ViewFile.Status.QUEUED;
        const stoppedSel = this._statusFilter.status === ViewFile.Status.STOPPED;
        const defaultSel = this._statusFilter.status === ViewFile.Status.DEFAULT;

        const filter: ViewFileFilter = new ViewFileFilter({
            extractedFilterEnabled: extractedEn,
            extractingFilterEnabled: extractingEn,
            downloadedFilterEnabled: downloadedEn,
            downloadingFilterEnabled: downloadingEn,
            queuedFilterEnabled: queuedEn,
            stoppedFilterEnabled: stoppedEn,
            defaultFilterEnabled: defaultEn,

            allFilterSelected: allSel,
            extractedFilterSelected: extractedSel,
            extractingFilterSelected: extractingSel,
            downloadedFilterSelected: downloadedSel,
            downloadingFilterSelected: downloadingSel,
            queuedFilterSelected: queuedSel,
            stoppedFilterSelected: stoppedSel,
            defaultFilterSelected: defaultSel,
        });
        this._logger.debug("Updated filter: %O", filter.toJS());
        this._filter.next(filter);
    }
}
